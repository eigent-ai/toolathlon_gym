from argparse import ArgumentParser

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_local import check_local  # uses iter_rows, str_match, lower() for content validation

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--groundtruth_workspace", required=False)
    parser.add_argument("--res_log_file", required=False, help="Path to result log file")
    parser.add_argument("--launch_time", required=False, help="Launch time")
    args = parser.parse_args()

    # Check local Excel output
    try:
        local_pass, local_error = check_local(args.agent_workspace, args.groundtruth_workspace)
        if not local_pass:
            print("local check failed: ", local_error)
            sys.exit(1)
    except Exception as e:
        print("local check error: ", e)
        sys.exit(1)

    print("Pass all tests!")
