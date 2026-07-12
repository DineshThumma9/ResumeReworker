"""
utils/error_helpers.py
-----------------------
Shared LLM/API error classification used for SSE error events.
Keeps error-message formatting consistent across all streaming endpoints.
"""


def classify_llm_error(
    error: Exception, dev_mode: bool = False, tb: str | None = None
) -> str:
    """
    Map a raw exception from an LLM call to a user-facing error string.
    Checks standard attributes (like status_code or code) used by
    OpenAI, Mistral, Gemini, Groq, and HTTPX to provide accurate messages.
    """
    status_code = None

    # Dynamically extract status code if the provider's exception includes it
    if hasattr(error, "status_code"):
        status_code = error.status_code
    elif hasattr(error, "code"):
        status_code = error.code
    elif hasattr(error, "response") and hasattr(error.response, "status_code"):
        status_code = error.response.status_code

    # Convert status_code to integer if possible
    if status_code is not None:
        try:
            status_code = int(status_code)
        except (ValueError, TypeError):
            status_code = None

    if status_code == 429:
        err_msg = "API Error: You have exceeded your API quota or rate limit. Please check your billing or plan."
    elif status_code == 402:
        err_msg = "API Error: Payment is required. Please check your billing details on your provider's dashboard."
    elif status_code in (401, 403):
        err_msg = "API Error: Invalid or unauthorized API key. Please check your API key in Settings."
    else:
        # Fallback to string heuristics for cases where status code isn't easily extracted
        msg = str(error)
        if (
            "429" in msg
            or "RESOURCE_EXHAUSTED" in msg
            or "quota" in msg.lower()
            or "rate limit" in msg.lower()
        ):
            err_msg = "API Error: You have exceeded your API quota or rate limit. Please check your billing or plan."
        elif (
            "402" in msg
            or "payment required" in msg.lower()
            or "insufficient_quota" in msg.lower()
        ):
            err_msg = "API Error: Payment is required. Please check your billing details on your provider's dashboard."
        elif (
            "401" in msg
            or "403" in msg
            or "API_KEY" in msg
            or "unauthorized" in msg.lower()
            or "invalid api key" in msg.lower()
        ):
            err_msg = "API Error: Invalid or unauthorized API key. Please check your API key in Settings."
        else:
            err_msg = f"Internal Error: {msg}"
            if not dev_mode:
                err_msg += "\nPlease try again or contact support."

    if dev_mode and tb:
        err_msg += f"\nTraceback:\n{tb}"
    return err_msg
