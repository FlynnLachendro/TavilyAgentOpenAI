# OpenAI Tavily Agent

An `openai-agents` SDK agent that implements the [Agent2Agent (A2A) Protocol](https://google-a2a.github.io/A2A/) with access to the [Tavily Search API](https://www.tavily.com/).

This repository was created for the [Agent2Agent (A2A) UI](https://github.com/A2ANet/A2AUI) and shows an A2A-compatible agent using OpenAI's native agent framework.

## Installation & Usage

### Local A2A Server

To use the OpenAI Tavily Agent with the A2A protocol:

1.  Clone the repository: `git clone https://github.com/FlynnLachendro/TavilyAgentOpenAI.git`
2.  `cd TavilyAgentOpenAI`
3.  Create an `.env` file. A `.env.example` is provided for reference.
4.  Set `OPENAI_API_KEY` and `TAVILY_API_KEY` in your `.env` file.
5.  Install `uv` and `pyenv` if you haven't already.
6.  Set up the virtual environment and install dependencies:
    ```bash
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
    ```
7.  Run the A2A server using `uv` which will load the `.env` file:
    ```bash
    uv run --env-file .env main.py
    ```
    The server will be available at `http://localhost:9998`.

### CLI Dev Mode

To test the core agent logic directly in your terminal without the A2A server:

1.  Complete steps 1-6 from the "Local A2A Server" section above.
2.  Run the agent's command-line interface:
    ```bash
    uv run --env-file .env test_agent.py
    ```

This allows for quick interaction with the agent's internal workings.

### Docker A2A Server

To run the agent using Docker:

1.  Clone the repository.
2.  Build the Docker image: `docker build -t openai-tavily-agent .`
3.  Run the container, providing your API keys as environment variables:

    ```bash
    docker run --rm -p 9998:8080 \
      -e TAVILY_API_KEY='your_tavily_api_key' \
      -e OPENAI_API_KEY='your_openai_api_key' \
      openai-tavily-agent
    ```

    _Note: The container exposes port 8080 internally, which we map to 9998 on the host machine._

The server will start on `http://localhost:9998`.

## Deployment

You can deploy the containerised agent to various cloud platforms.

### Google Cloud Run

To deploy the agent (and set up continuous deployment) with Google Cloud Run:

1.  Fork this repository.
2.  Go to [https://cloud.google.com/](https://cloud.google.com/)
3.  Create or select a project and enable billing.
4.  Search for "Cloud Run".
5.  Click "Connect repo".
6.  Select "Continuously deploy from a repository (source or function)".
7.  Click "Set up with Cloud Build".
8.  Select your forked repository > click "Next".
9.  Select "Dockerfile" > click "Save".
10. Under "Authentication", select "Allow unauthenticated invocations".
11. Copy the "Endpoint URL" that is generated.
12. Expand "Containers, Volumes, Networking, Security" > go to "Variables & Secrets" > click "Add variable".
13. Set "Name" to `SERVICE_URL` and "Value" to the copied "Endpoint URL".
14. Under "Secrets exposed as environment variables", click "Reference a secret".
15. Set "Name" to `OPENAI_API_KEY`. Click "Secret" > "Create new secret", name it `OPENAI_API_KEY`, and paste your secret value. Set "Version" to "latest".
16. Click "Reference a secret" again.
17. Set "Name" to `TAVILY_API_KEY`. Create a new secret named `TAVILY_API_KEY` with your key and set "Version" to "latest".
18. Click "Done", then click "Create".
19. The first deployment might fail due to permissions. In the error message, copy the revision service account email (e.g., "XXXXXXXXXXXX-compute@developer.gserviceaccount.com").
20. Go to "Secret Manager", select both the `OPENAI_API_KEY` and `TAVILY_API_KEY` secrets.
21. In the right-hand permissions panel, click "ADD PRINCIPAL".
22. Paste the service account email as the "New principal".
23. Select the role "Secret Manager Secret Accessor".
24. Click "Save".
25. Go back to "Cloud Run" and "Edit & deploy new revision" > Click "Deploy".

The agent should now be deployed successfully!

#### Retrieve the Agent Card

1.  Copy the service "URL" from your Cloud Run service page.
2.  Open a new tab, paste the URL, and add `/.well-known/agent.json` to the end.
3.  You should see the raw JSON of the Agent Card.

#### Connect with the A2A UI

1.  Run the [Agent2Agent (A2A) UI](https://github.com/A2ANet/A2AUI) locally.
2.  Click "+ Agent" and paste your public Cloud Run URL (e.g. `https://openai-tavily-agent-XXXXXXXXXXXX.region.run.app`).
3.  Send a message. You should get a response from your cloud-hosted agent!

The agent is now set up to automatically redeploy when changes are pushed to the main branch of your forked repo.
