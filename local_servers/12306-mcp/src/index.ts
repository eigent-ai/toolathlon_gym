#!/usr/bin/env node

// PostgreSQL-backed 12306 MCP server
// All API calls to kyfw.12306.cn are replaced with local PostgreSQL queries.

import { program } from 'commander';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { format } from 'date-fns';
import { toZonedTime } from 'date-fns-tz';
import pg from 'pg';
import {
    StationData,
    StationDataKeys,
    TicketInfo,
    RouteStationInfo,
    Price,
} from './types.js';

const { Pool } = pg;

const VERSION = '0.3.5-pg';

// PostgreSQL pool
const pool = new Pool({
    host: process.env.PG_HOST || 'localhost',
    port: parseInt(process.env.PG_PORT || '5432'),
    database: process.env.PG_DATABASE || 'toolathlon',
    user: process.env.PG_USER || 'postgres',
    password: process.env.PG_PASSWORD || 'postgres',
    idleTimeoutMillis: 10000,
});
pool.on('error', () => { /* swallow idle connection errors */ });

// ---------------------------------------------------------------------------
// Station dictionaries (loaded from PostgreSQL at startup)
// ---------------------------------------------------------------------------
let STATIONS: Record<string, StationData> = {};
let CITY_STATIONS: Record<string, { station_code: string; station_name: string }[]> = {};
let CITY_CODES: Record<string, { station_code: string; station_name: string }> = {};
let NAME_STATIONS: Record<string, { station_code: string; station_name: string }> = {};

async function loadStations(): Promise<void> {
    const result = await pool.query(
        `SELECT station_code, station_name, station_pinyin, station_short, city,
                station_id, station_index, code, r1, r2
         FROM train.stations`
    );
    STATIONS = {};
    CITY_STATIONS = {};
    CITY_CODES = {};
    NAME_STATIONS = {};
    for (const row of result.rows) {
        const station = row as StationData;
        STATIONS[station.station_code] = station;
        // CITY_STATIONS
        if (!CITY_STATIONS[station.city]) CITY_STATIONS[station.city] = [];
        CITY_STATIONS[station.city].push({ station_code: station.station_code, station_name: station.station_name });
        // CITY_CODES: prefer station whose name == city
        if (station.station_name === station.city || !CITY_CODES[station.city]) {
            CITY_CODES[station.city] = { station_code: station.station_code, station_name: station.station_name };
        }
        // NAME_STATIONS
        NAME_STATIONS[station.station_name] = { station_code: station.station_code, station_name: station.station_name };
    }
}

// ---------------------------------------------------------------------------
// Seat type constants (kept from original)
// ---------------------------------------------------------------------------
const SEAT_TYPES: Record<string, { name: string; short: string }> = {
    '9': { name: '商务座', short: 'swz' },
    P: { name: '特等座', short: 'tz' },
    M: { name: '一等座', short: 'zy' },
    O: { name: '二等座', short: 'ze' },
    '6': { name: '高级软卧', short: 'gr' },
    '4': { name: '软卧', short: 'rw' },
    F: { name: '动卧', short: 'rw' },
    '3': { name: '硬卧', short: 'yw' },
    '2': { name: '软座', short: 'rz' },
    '1': { name: '硬座', short: 'yz' },
    W: { name: '无座', short: 'wz' },
    H: { name: '其他', short: 'qt' },
};

function formatTicketStatus(num: string): string {
    if (num.match(/^\d+$/)) {
        const count = parseInt(num);
        return count === 0 ? '无票' : `剩余${count}张票`;
    }
    switch (num) {
        case '有': case '充足': return '有票';
        case '无': case '--': case '': return '无票';
        case '候补': return '无票需候补';
        default: return `${num}票`;
    }
}

function formatTicketsInfo(ticketsInfo: TicketInfo[]): string {
    if (ticketsInfo.length === 0) return '没有查询到相关车次信息';
    let result = '车次 | 出发站 -> 到达站 | 出发时间 -> 到达时间 | 历时\n';
    for (const ti of ticketsInfo) {
        let s = `${ti.start_train_code}(实际车次train_no: ${ti.train_no}) ${ti.from_station}(telecode: ${ti.from_station_telecode}) -> ${ti.to_station}(telecode: ${ti.to_station_telecode}) ${ti.start_time} -> ${ti.arrive_time} 历时：${ti.lishi}`;
        for (const price of ti.prices) {
            s += `\n- ${price.seat_name}: ${formatTicketStatus(price.num)} ${price.price}元`;
        }
        result += `${s}\n`;
    }
    return result;
}

function formatTicketsInfoCSV(ticketsInfo: TicketInfo[]): string {
    if (ticketsInfo.length === 0) return '没有查询到相关车次信息';
    let result = '车次,实际车次train_no,出发站,到达站,出发时间,到达时间,历时,票价信息,特色标签\n';
    for (const ti of ticketsInfo) {
        let priceStr = '[';
        for (const p of ti.prices) priceStr += `${p.seat_name}: ${formatTicketStatus(p.num)}${p.price}元,`;
        priceStr += ']';
        result += `${ti.start_train_code},${ti.train_no},${ti.from_station}(telecode:${ti.from_station_telecode}),${ti.to_station}(telecode:${ti.to_station_telecode}),${ti.start_time},${ti.arrive_time},${ti.lishi},${priceStr},${ti.dw_flag.join('&') || '/'}\n`;
    }
    return result;
}

const TIME_COMPARATORS: Record<string, (a: TicketInfo, b: TicketInfo) => number> = {
    startTime: (a, b) => {
        const [ah, am] = a.start_time.split(':').map(Number);
        const [bh, bm] = b.start_time.split(':').map(Number);
        return ah * 60 + am - (bh * 60 + bm);
    },
    arriveTime: (a, b) => {
        const [ah, am] = a.arrive_time.split(':').map(Number);
        const [bh, bm] = b.arrive_time.split(':').map(Number);
        return ah * 60 + am - (bh * 60 + bm);
    },
    duration: (a, b) => {
        const [ah, am] = a.lishi.split(':').map(Number);
        const [bh, bm] = b.lishi.split(':').map(Number);
        return ah * 60 + am - (bh * 60 + bm);
    },
};

function filterTicketsInfo(
    tickets: TicketInfo[],
    trainFilterFlags: string,
    earliestStartTime = 0,
    latestStartTime = 24,
    sortFlag = '',
    sortReverse = false,
    limitedNum = 0
): TicketInfo[] {
    let result = trainFilterFlags
        ? tickets.filter(t => {
              for (const flag of trainFilterFlags) {
                  if (flag === 'G' && (t.start_train_code.startsWith('G') || t.start_train_code.startsWith('C'))) return true;
                  if (flag === 'D' && t.start_train_code.startsWith('D')) return true;
                  if (flag === 'Z' && t.start_train_code.startsWith('Z')) return true;
                  if (flag === 'T' && t.start_train_code.startsWith('T')) return true;
                  if (flag === 'K' && t.start_train_code.startsWith('K')) return true;
              }
              return false;
          })
        : tickets;
    result = result.filter(t => {
        const h = parseInt(t.start_time.split(':')[0], 10);
        return h >= earliestStartTime && h < latestStartTime;
    });
    if (sortFlag && TIME_COMPARATORS[sortFlag]) {
        result.sort(TIME_COMPARATORS[sortFlag]);
        if (sortReverse) result.reverse();
    }
    return limitedNum > 0 ? result.slice(0, limitedNum) : result;
}

function checkDate(date: string): boolean {
    return true; // date check disabled — mock data uses historical dates
}

// ---------------------------------------------------------------------------
// Query tickets from PostgreSQL
// ---------------------------------------------------------------------------
async function queryTickets(date: string, fromStation: string, toStation: string): Promise<TicketInfo[]> {
    const result = await pool.query(
        `SELECT t.id, t.train_no, t.station_train_code, t.from_station_telecode, t.to_station_telecode,
                t.start_time, t.arrive_time, t.lishi, t.dw_flags,
                sf.station_name AS from_name, st.station_name AS to_name
         FROM train.trains t
         JOIN train.stations sf ON sf.station_code = t.from_station_telecode
         JOIN train.stations st ON st.station_code = t.to_station_telecode
         WHERE t.from_station_telecode = $1
           AND t.to_station_telecode = $2
           AND t.depart_date = $3`,
        [fromStation, toStation, date]
    );

    const tickets: TicketInfo[] = [];
    for (const row of result.rows) {
        const seatsResult = await pool.query(
            `SELECT seat_type_code, seat_name, seat_short, num, price, discount
             FROM train.train_seats WHERE train_id = $1`,
            [row.id]
        );
        const prices: Price[] = seatsResult.rows.map(s => ({
            seat_name: s.seat_name,
            short: s.seat_short,
            seat_type_code: s.seat_type_code,
            num: s.num,
            price: parseFloat(s.price),
            discount: s.discount,
        }));
        tickets.push({
            train_no: row.train_no,
            start_train_code: row.station_train_code,
            start_date: date,
            arrive_date: date,
            start_time: row.start_time,
            arrive_time: row.arrive_time,
            lishi: row.lishi,
            from_station: row.from_name,
            to_station: row.to_name,
            from_station_telecode: row.from_station_telecode,
            to_station_telecode: row.to_station_telecode,
            prices,
            dw_flag: row.dw_flags ? row.dw_flags.split('#').filter((f: string) => f && f !== '0') : [],
        });
    }
    return tickets;
}

// ---------------------------------------------------------------------------
// MCP Server
// ---------------------------------------------------------------------------
export const server = new McpServer({
    name: '12306-mcp',
    version: VERSION,
    capabilities: { resources: {}, tools: {} },
    instructions: '该服务用于查询中国铁路火车票信息（本地模拟数据）。',
});

server.resource('stations', 'data://all-stations', async (uri) => ({
    contents: [{ uri: uri.href, text: JSON.stringify(STATIONS) }],
}));

server.tool(
    'get-current-date',
    '获取当前日期，以上海时区（Asia/Shanghai, UTC+8）为准，返回格式为 "yyyy-MM-dd"。主要用于解析用户提到的相对日期（如“明天”、“下周三”），为其他需要日期的接口提供准确的日期输入。',
    {},
    async () => {
        const nowInShanghai = toZonedTime(new Date(), 'Asia/Shanghai');
        return { content: [{ type: 'text', text: format(nowInShanghai, 'yyyy-MM-dd') }] };
    }
);

server.tool(
    'get-stations-code-in-city',
    '通过中文城市名查询该城市 **所有** 火车站的名称及其对应的 `station_code`，结果是一个包含多个车站信息的列表。',
    { city: z.string().describe('中文城市名称，例如："北京", "上海"') },
    async ({ city }) => {
        if (!(city in CITY_STATIONS)) return { content: [{ type: 'text', text: 'Error: City not found.' }] };
        return { content: [{ type: 'text', text: JSON.stringify(CITY_STATIONS[city]) }] };
    }
);

server.tool(
    'get-station-code-of-citys',
    '通过中文城市名查询代表该城市的 `station_code`。此接口主要用于在用户提供**城市名**作为出发地或到达地时，为接口准备 `station_code` 参数。',
    { citys: z.string().describe('要查询的城市，比如"北京"。若要查询多个城市，请用|分割，比如"北京|上海"。') },
    async ({ citys }) => {
        const result: Record<string, object> = {};
        for (const city of citys.split('|')) {
            result[city] = city in CITY_CODES ? CITY_CODES[city] : { error: '未检索到城市。' };
        }
        return { content: [{ type: 'text', text: JSON.stringify(result) }] };
    }
);

server.tool(
    'get-station-code-by-names',
    '通过具体的中文车站名查询其 `station_code` 和车站名。此接口主要用于在用户提供**具体车站名**作为出发地或到达地时，为接口准备 `station_code` 参数。',
    { stationNames: z.string().describe('具体的中文车站名称，例如："北京南", "上海虹桥"。若要查询多个站点，请用|分割，比如"北京南|上海虹桥"。') },
    async ({ stationNames }) => {
        const result: Record<string, object> = {};
        for (const name of stationNames.split('|')) {
            result[name] = name in NAME_STATIONS ? NAME_STATIONS[name] : { error: '未检索到车站。' };
        }
        return { content: [{ type: 'text', text: JSON.stringify(result) }] };
    }
);

server.tool(
    'get-station-by-telecode',
    '通过车站的 `station_telecode` 查询车站的详细信息，包括名称、拼音、所属城市等。此接口主要用于在已知 `telecode` 的情况下获取更完整的车站数据，或用于特殊查询及调试目的。一般用户对话流程中较少直接触发。',
    { stationTelecode: z.string().describe('车站的 `station_telecode` (3位字母编码)') },
    async ({ stationTelecode }) => {
        if (!STATIONS[stationTelecode]) return { content: [{ type: 'text', text: 'Error: Station not found.' }] };
        return { content: [{ type: 'text', text: JSON.stringify(STATIONS[stationTelecode]) }] };
    }
);

server.tool(
    'get-tickets',
    '查询12306余票信息。',
    {
        date: z.string().length(10).describe('查询日期，格式为 "yyyy-MM-dd"。如果用户提供的是相对日期（如“明天”），请务必先调用 `get-current-date` 接口获取当前日期，并计算出目标日期。'),
        fromStation: z.string().describe('出发地的 `station_code` 。必须是通过 `get-station-code-by-names` 或 `get-station-code-of-citys` 接口查询得到的编码，严禁直接使用中文地名。'),
        toStation: z.string().describe('到达地的 `station_code` 。必须是通过 `get-station-code-by-names` 或 `get-station-code-of-citys` 接口查询得到的编码，严禁直接使用中文地名。'),
        trainFilterFlags: z.string().regex(/^[GDZTKOFS]*$/).max(8).optional().default('').describe('车次筛选条件，默认为空，即不筛选。支持多个标志同时筛选。例如用户说“高铁票”，则应使用 "G"。可选标志：[G(高铁/城际),D(动车),Z(直达特快),T(特快),K(快速),O(其他),F(复兴号),S(智能动车组)]'),
        earliestStartTime: z.number().min(0).max(24).optional().default(0).describe('最早出发时间（0-24），默认为0。'),
        latestStartTime: z.number().min(0).max(24).optional().default(24).describe('最迟出发时间（0-24），默认为24。'),
        sortFlag: z.string().optional().default('').describe('排序方式，默认为空，即不排序。仅支持单一标识。可选标志：[startTime(出发时间从早到晚), arriveTime(抵达时间从早到晚), duration(历时从短到长)]'),
        sortReverse: z.boolean().optional().default(false).describe('是否逆向排序结果，默认为false。仅在设置了sortFlag时生效。'),
        limitedNum: z.number().min(0).optional().default(0).describe('返回的余票数量限制，默认为0，即不限制。'),
        csvFormat: z.boolean().default(false).optional().describe('是否使用CSV格式返回。'),
    },
    async ({ date, fromStation, toStation, trainFilterFlags, earliestStartTime, latestStartTime, sortFlag, sortReverse, limitedNum, csvFormat }) => {
        if (!checkDate(date)) return { content: [{ type: 'text', text: 'Error: The date cannot be earlier than today.' }] };
        if (!STATIONS[fromStation] || !STATIONS[toStation]) return { content: [{ type: 'text', text: 'Error: Station not found.' }] };
        const tickets = await queryTickets(date, fromStation, toStation);
        const filtered = filterTicketsInfo(tickets, trainFilterFlags || '', earliestStartTime, latestStartTime, sortFlag || '', sortReverse, limitedNum);
        const text = csvFormat ? formatTicketsInfoCSV(filtered) : formatTicketsInfo(filtered);
        return { content: [{ type: 'text', text }] };
    }
);

server.tool(
    'get-interline-tickets',
    '查询12306中转余票信息。尚且只支持查询前十条。',
    {
        date: z.string().length(10).describe('查询日期，格式为 "yyyy-MM-dd"。如果用户提供的是相对日期（如“明天”），请务必先调用 `get-current-date` 接口获取当前日期，并计算出目标日期。'),
        fromStation: z.string().describe('出发地的 `station_code` 。必须是通过 `get-station-code-by-names` 或 `get-station-code-of-citys` 接口查询得到的编码，严禁直接使用中文地名。'),
        toStation: z.string().describe('出发地的 `station_code` 。必须是通过 `get-station-code-by-names` 或 `get-station-code-of-citys` 接口查询得到的编码，严禁直接使用中文地名。'),
        middleStation: z.string().optional().default('').describe('中转地的 `station_code` ，可选。必须是通过 `get-station-code-by-names` 或 `get-station-code-of-citys` 接口查询得到的编码，严禁直接使用中文地名。'),
        showWZ: z.boolean().optional().default(false).describe('是否显示无座车，默认不显示无座车。'),
        trainFilterFlags: z.string().regex(/^[GDZTKOFS]*$/).max(8).optional().default('').describe('车次筛选条件，默认为空。从以下标志中选取多个条件组合[G(高铁/城际),D(动车),Z(直达特快),T(特快),K(快速),O(其他),F(复兴号),S(智能动车组)]'),
        earliestStartTime: z.number().min(0).max(24).optional().default(0).describe('最早出发时间（0-24），默认为0。'),
        latestStartTime: z.number().min(0).max(24).optional().default(24).describe('最迟出发时间（0-24），默认为24。'),
        sortFlag: z.string().optional().default('').describe('排序方式，默认为空，即不排序。仅支持单一标识。可选标志：[startTime(出发时间从早到晚), arriveTime(抵达时间从早到晚), duration(历时从短到长)]'),
        sortReverse: z.boolean().optional().default(false).describe('是否逆向排序结果，默认为false。仅在设置了sortFlag时生效。'),
        limitedNum: z.number().min(1).optional().default(10).describe('返回的中转余票数量限制，默认为10。'),
    },
    async ({ date, fromStation, toStation, middleStation, trainFilterFlags, earliestStartTime, latestStartTime, sortFlag, sortReverse, limitedNum }) => {
        if (!checkDate(date)) return { content: [{ type: 'text', text: 'Error: The date cannot be earlier than today.' }] };

        // Find all possible middle stations that have trains from fromStation and to toStation
        const midResult = await pool.query(
            `SELECT DISTINCT t1.to_station_telecode AS mid
             FROM train.trains t1
             JOIN train.trains t2 ON t1.to_station_telecode = t2.from_station_telecode
             WHERE t1.from_station_telecode = $1
               AND t2.to_station_telecode = $2
               AND t1.depart_date = $3 AND t2.depart_date = $3
               ${middleStation ? 'AND t1.to_station_telecode = $4' : ''}
             LIMIT 5`,
            middleStation ? [fromStation, toStation, date, middleStation] : [fromStation, toStation, date]
        );

        if (midResult.rows.length === 0) {
            return { content: [{ type: 'text', text: '很抱歉，未查到相关的中转余票信息。' }] };
        }

        let output = '出发时间 -> 到达时间 | 出发车站 -> 中转车站 -> 到达车站 | 换乘标志 |换乘等待时间| 总历时\n\n';
        let count = 0;
        for (const { mid } of midResult.rows) {
            if (count >= limitedNum) break;
            const leg1 = await queryTickets(date, fromStation, mid);
            const leg2 = await queryTickets(date, mid, toStation);
            const midStation = STATIONS[mid];
            const midName = midStation?.station_name || mid;
            for (const t1 of leg1.slice(0, 3)) {
                for (const t2 of leg2.slice(0, 3)) {
                    if (count >= limitedNum) break;
                    const fromName = STATIONS[fromStation]?.station_name || fromStation;
                    const toName = STATIONS[toStation]?.station_name || toStation;
                    output += `${date} ${t1.start_time} -> ${date} ${t2.arrive_time} | `;
                    output += `${fromName} -> ${midName} -> ${toName} | 同站换乘 | - | -\n\n`;
                    output += '\t第一段: ' + t1.start_train_code + ' ' + t1.start_time + ' -> ' + t1.arrive_time + '\n';
                    output += '\t第二段: ' + t2.start_train_code + ' ' + t2.start_time + ' -> ' + t2.arrive_time + '\n\n';
                    count++;
                }
            }
        }
        return { content: [{ type: 'text', text: output }] };
    }
);

server.tool(
    'get-train-route-stations',
    '查询特定列车车次在指定区间内的途径车站、到站时间、出发时间及停留时间等详细经停信息。当用户询问某趟具体列车的经停站时使用此接口。',
    {
        trainNo: z.string().describe('要查询的实际车次编号 `train_no`，例如 "240000G10336"，而非"G1033"。此编号通常可以从 `get-tickets` 的查询结果中获取，或者由用户直接提供。'),
        fromStationTelecode: z.string().describe('该列车行程的**出发站**的 `station_telecode` (3位字母编码`)。通常来自 `get-tickets` 结果中的 `telecode` 字段，或者通过 `get-station-code-by-names` 得到。'),
        toStationTelecode: z.string().describe('该列车行程的**到达站**的 `station_telecode` (3位字母编码)。通常来自 `get-tickets` 结果中的 `telecode` 字段，或者通过 `get-station-code-by-names` 得到。'),
        departDate: z.string().length(10).describe('列车从 `fromStationTelecode` 指定的车站出发的日期 (格式: yyyy-MM-dd)。如果用户提供的是相对日期，请务必先调用 `get-current-date` 解析。'),
    },
    async ({ trainNo }) => {
        const result = await pool.query(
            `SELECT station_no, station_telecode, station_name, arrive_time, depart_time, stopover_time
             FROM train.train_routes WHERE train_no = $1 ORDER BY station_no`,
            [trainNo]
        );
        if (result.rows.length === 0) return { content: [{ type: 'text', text: '未查询到相关车次信息。' }] };
        const routeInfo: RouteStationInfo[] = result.rows.map(r => ({
            arrive_time: r.arrive_time,
            station_name: r.station_name,
            stopover_time: r.stopover_time,
            station_no: r.station_no,
        }));
        return { content: [{ type: 'text', text: JSON.stringify(routeInfo) }] };
    }
);

// ---------------------------------------------------------------------------
// Startup
// ---------------------------------------------------------------------------
async function startServer() {
    await loadStations();
    console.error(`12306 MCP Server (pg-backed) started. Loaded ${Object.keys(STATIONS).length} stations.`);

    program
        .name('mcp-server-12306')
        .version(VERSION)
        .option('--stdio', 'use stdio transport (default)', true)
        .parse(process.argv);

    const transport = new StdioServerTransport();
    await server.connect(transport);
}

startServer().catch(err => {
    console.error('Failed to start server:', err);
    process.exit(1);
});
