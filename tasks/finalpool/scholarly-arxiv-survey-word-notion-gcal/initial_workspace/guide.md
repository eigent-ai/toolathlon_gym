# Literature Survey Organization Guide

## Taxonomy Categories for LLM Reasoning Methods

1. **Prompting-Based Methods**: Techniques that elicit reasoning through prompt design
   - Chain-of-Thought (CoT): step-by-step reasoning traces
   - Automatic CoT: automated prompt generation for reasoning

2. **Search-Based Methods**: Techniques that explore multiple reasoning paths
   - Tree of Thoughts (ToT): tree-structured exploration with backtracking
   - Self-Consistency: sampling diverse paths and majority voting

3. **Verification-Based Methods**: Techniques that validate reasoning steps
   - Process Supervision: reward models for step-by-step verification

## Comparison Criteria

For each method, evaluate along these dimensions:
- **Accuracy Improvement**: How much does it improve over baseline?
- **Computational Cost**: Additional inference cost (number of API calls, tokens)
- **Task Generality**: Range of tasks where the method applies
- **Implementation Complexity**: How easy is it to implement?

## Survey Structure Requirements

- Abstract: 150-200 words summarizing scope and findings
- Introduction: Motivation, scope, contributions of the survey
- Background: LLM basics, in-context learning, prompting
- Taxonomy: Organized by method category (see above)
- Comparative Analysis: Table with method, paper, accuracy, cost, generality
- Open Challenges: Limitations, unsolved problems, future directions
- Conclusion: Summary of key findings and recommendations
