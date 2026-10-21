## Article Description

Discover how I built Spark AI, an intent-aware AI assistant using Kiro, the Strands Agents SDK, and Strands Decider 2B. Learn how it selects appropriate tools for calculations, summarization, study planning, and other tasks through a reusable agentic workflow.

## Tags

- Artificial Intelligence
- Agentic AI
- AWS
- Strands Agents SDK
- Strands Decider 2B
- Kiro
- Amazon Bedrock
- Generative AI
- Developer Tools
- Hackathon

---

# Spark AI: Building an Intent-Aware AI Assistant with Strands Decider 2B and Kiro

*From Simple Prompts to Smart Actions.*

## Introduction

AI assistants can answer questions, but not every request should be
handled in exactly the same way. A calculation is best handled by a
deterministic calculator, a long passage benefits from summarization,
and a programming question may need a code-focused explanation. Sending
every request through a general-purpose language model can make it
harder to ensure that the right process is used for each task.

**Spark AI** explores a different approach: an intent-aware assistant
that selects a suitable tool or response path for a user's request.
Built for the AWS User Group Madurai Strands Decider hackathon, the
project combines the Strands Agents SDK with Strands Decider 2B and a
web interface designed to make the decision process visible.

Project repository:
https://github.com/kishoreofficial1204/spark-ai-agent

## The Problem: One Chat Flow Does Not Fit Every Task

Different requests have different needs:

-   A calculation should produce a reliable numerical result.
-   A document summary should preserve the important ideas in less
    space.
-   A rewriting request should improve the wording while retaining the
    meaning.
-   A study-planning request should produce an organized schedule.
-   A code question should explain the relevant logic.
-   A general question may not need a specialized tool at all.

Spark AI is designed to choose a suitable path instead of treating all
of these requests as identical. The goal is not simply to generate text,
but to make the handling of each request more appropriate to the task.

## What Is Spark AI?

Spark AI is an intent-aware AI productivity assistant. Its supported
workflows include:

-   **Calculator:** Handles mathematical expressions through a safe,
    deterministic evaluator.
-   **Summarizer:** Produces short, detailed, or bullet-point summaries.
-   **Text Rewriter:** Reworks text into a more professional style.
-   **Study Planner:** Creates structured study schedules from a user's
    requirements.
-   **Code Explainer:** Helps users understand code.
-   **General response:** Answers requests that do not require a
    specialized tool.

The interface includes a decision panel that shows the selected tool,
the Decider's confidence, and a probability breakdown. This visibility
is useful for understanding why a particular path was chosen.

## Technology Stack

The repository documents the following core components:

-   **Strands Agents SDK:** Orchestrates the agent and its tools.
-   **Strands Decider 2B:** Supports the tool-selection decision before
    the language model handles the request.
-   **Amazon Bedrock with Nova Pro:** Provides the configured generative
    model for the agent.
-   **Python and FastAPI:** Power the backend API.
-   **React, TypeScript, Vite, and Tailwind CSS:** Build the web
    interface.
-   **Amazon Bedrock AgentCore Runtime:** The repository's documented
    deployment target.

The hackathon-provided hosted API is used for Decider access according
to the project's configuration. Model credentials and other secrets
should remain in environment variables or the relevant secure
configuration, never in frontend code or public source files.

## How the Agentic Decision Pattern Works

Spark AI uses a reusable tool-selection pattern documented in the
repository as `#tool-selection`, implemented in
`decider_kit/patterns/tool_selection.py`.

At a high level, the request flow is:

1.  **Receive the request.** The user submits a message through the
    Spark AI interface.
2.  **Evaluate the tool choice.** Strands Decider 2B evaluates a typed
    choice question to identify the tool most suitable for the request.
3.  **Apply the confidence rule.** The documented pattern uses a
    confidence threshold of 0.6. When confidence meets or exceeds the
    threshold, the agent starts with the selected tool. When confidence
    is lower, all available tools are passed to the language model so it
    has more flexibility.
4.  **Run the agent.** The Strands agent uses the available tool or
    tools to process the request.
5.  **Return the result.** The response is shown to the user, while the
    decision panel helps explain the selected path.

This approach separates the decision about *which tool is appropriate*
from the model's task of generating a response. The calculator is an
example of why that separation matters: arithmetic can be evaluated
deterministically instead of relying on a language model to guess the
result.

The confidence threshold is a routing rule, not a guarantee that every
decision is correct. The system should still be tested with varied and
ambiguous prompts, and its results should be reviewed.

### Architecture at a Glance

``` mermaid
flowchart TD
    U[User request] --> UI[React web interface]
    UI --> API[FastAPI backend]
    API --> D[Strands Decider 2B]
    D -->|Confident tool choice| T[Selected tool]
    D -->|Low confidence| A[Strands agent with available tools]
    T --> A
    A --> M[Amazon Bedrock model when needed]
    M --> R[Response and decision details]
    A --> R
    R --> UI
```

*Architecture overview based on the repository's documented components.
Exact runtime behavior can vary by request and tool.*

## A Walk Through the Demo

The demo video shows Spark AI's dark-themed interface and its decision
panel while requests are submitted. It demonstrates examples including:

### 1. Calculation

The prompt `What is 847 * 23?` is routed to the Calculator. The result
is calculated by the evaluator, making this a good example of using a
dedicated tool for a task that has a verifiable answer.

### 2. Summarization

A summarization request is routed to the Summarizer, which returns a
structured summary. The decision panel indicates the selected workflow,
allowing viewers to see that the request was handled differently from
the calculation.

### 3. Study Planning

A request to create a study plan for Math and Physics over five days is
routed to the Study Planner. The response is organized as a day-by-day
schedule based on the supplied constraints.

Together, these examples illustrate the project's central idea: a single
interface can direct different kinds of requests to different workflows.

## Building the Project with Kiro

Kiro was used as the development environment for building Spark AI. An
AI-assisted development workflow can help turn a product idea into a
structured specification, create and refine application components, and
iterate on implementation details.

The important engineering step is to review generated code and validate
it against the project's real requirements. In an agentic application,
this includes verifying the Decider integration, checking that tools
execute as expected, protecting API credentials, and testing the
end-to-end request flow. The repository contains the project code and
setup instructions so that the implementation can be inspected and
reproduced.

## Running Spark AI Locally

Use the repository's README as the source of truth for current setup
instructions:

1.  Clone the repository:

    ``` bash
    git clone https://github.com/kishoreofficial1204/spark-ai-agent.git
    cd spark-ai-agent
    ```

2.  Create a local environment file from the example:

    ``` bash
    cp .env.example .env
    ```

    On Windows, copy `.env.example` to `.env` using File Explorer or the
    appropriate shell command. Add the required credentials using the
    project's documented configuration. Never commit the populated
    `.env` file.

3.  Install backend dependencies and start the API:

    ``` bash
    pip install -r backend/requirements.txt
    cd backend
    python main.py
    ```

4.  In a separate terminal, install frontend dependencies and start the
    development server:

    ``` bash
    cd frontend
    npm install
    npm run dev
    ```

5.  Open the local frontend URL printed by the development server. The
    repository README currently documents `http://localhost:5173` for
    the frontend and `http://localhost:8000` for the backend.

The project README also documents the hackathon kit's demo, benchmark,
and deployment commands. Check the current repository instructions and
environment requirements before running them, because model access and
deployment depend on the relevant credentials and configuration.

## Security and Reliability Considerations

Agentic workflows need clear boundaries. Spark AI should keep API keys
on the backend, validate incoming requests, and avoid exposing
credentials in logs or UI messages. Tools should be designed for the
task they perform; for example, a calculator should reject invalid
expressions safely rather than evaluate arbitrary code.

Decision confidence is useful for routing, but it is not proof of
correctness. Testing should include ordinary requests, ambiguous
prompts, invalid input, tool errors, and model or network failures. The
interface should communicate failures honestly rather than displaying
fabricated results.

## Lessons and Future Improvements

Spark AI provides a practical example of how an explicit decision layer
can complement an agent framework. Its visible decision panel helps make
tool selection easier to inspect, while its collection of specialized
workflows shows how the same interface can support multiple task types.

Potential next steps include expanding the automated evaluation set,
measuring tool-selection quality on held-out examples, improving
clarification behavior for ambiguous prompts, and documenting deployment
and operational monitoring. These should be treated as future
improvements unless the corresponding work has already been completed
and verified.

## Conclusion

Spark AI explores a simple but useful idea: an AI assistant should not
only respond to a prompt; it should also choose an appropriate way to
handle it. By combining Strands Decider 2B's tool-selection role with
the Strands Agents SDK and task-specific tools, the project demonstrates
an intent-aware workflow for everyday productivity tasks.

The project was built with Kiro and is available publicly so developers
can inspect the implementation and experiment with the approach.

**Spark AI --- From Simple Prompts to Smart Actions.**

## Project Resources

-   **GitHub repository:**
    https://github.com/kishoreofficial1204/spark-ai-agent
-   **Live application:** https://spark-ai-agent-red.vercel.app
-   **Demo video:** Add the public URL to the uploaded demo video after
    publishing it to a publicly accessible platform.
-   **License:** Apache-2.0

------------------------------------------------------------------------

*Editorial note before publication: verify that the live application,
model configuration, setup commands, and each demonstrated feature still
work with the current repository revision. Add the public demo video
link and any required AWS Builder Center metadata before publishing.*
