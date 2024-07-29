# from agentforge.llm.gemini import Gemini
#
# claude = Gemini('gemini-1.5-flash-latest') # Model name goes here
from agentforge.llm.anthropic import Claude

claude = Claude('claude-3-opus-20240229')

prompt = ['test','test']
params = {
    "max_new_tokens": 4000,
    "temperature": 0.5,
    "top_p": 0.1
}

var = claude.generate_text(prompt, **params)

print(var)
