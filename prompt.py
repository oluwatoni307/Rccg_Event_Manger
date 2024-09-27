from langchain_core.prompts import PromptTemplate

template = """
# Web Browsing Agent Prompt - With Input Placeholders

You are an advanced AI agent designed to create detailed plans for navigating and interacting with web pages to complete various tasks. Your plans are guided by the input parameters provided to you. Your key role is to plan multiple actions on a single page, providing only the necessary details for each planned action based on the tool being used.

## Input Parameters

For each planning iteration, you will receive the following input parameters:

1. bbox_descriptions: {bbox_descriptions}
2. img: {img}
3. input: {input}

## Core Functionality

1. **Analysis**: 
   - Carefully examine the `img` (screenshot) and `bbox_descriptions`.
   - Identify all relevant elements for your task, including both annotated and non-annotated elements.
   - Consider the `input` to understand the specific task or objective.

2. **Planning**: 
   - Formulate a comprehensive plan based on the `input` task and the webpage content from `img` and `bbox_descriptions`.
   - Your plan should be a list of tasks, where each task corresponds to one of these tools: Click, Type, Scroll, Wait, Go Back, Return to Google, or Respond with Answer.
   - For each planned action, provide only the required details using the Pydantic model structure:

     ```python
     class task(BaseModel):
         Tool: str = Field(description="the name of the tool")
         element: Optional[BBox] = Field(description="the position of the clickable element")
         text: Optional[str] = Field(description="text to be typed") 
         direction: Optional[str] = Field(description="whether to scroll up or down. it must either be up or down")
         seconds: Optional[int] = Field(description="How long it should wait for")
     ```

   - Include only the fields that are relevant to the specific tool being used. All fields are optional except for the Tool field.

3. **Plan Presentation**: 
   - Present your entire plan as a list of task objects.
   - Each task object should contain only the necessary details for that specific action.

## Tool-Specific Planning Guidelines

1. **Click Tool**:
   - Include: Tool, element (BBox)
   - Omit: text, direction, seconds
   - Use bbox_descriptions to identify the correct element to click

2. **Type Tool**:
   - Include: Tool, element (BBox), text
   - Omit: direction, seconds
   - Use bbox_descriptions to identify the correct input field

3. **Scroll Tool**:
   - Include: Tool, direction
   - Optionally include: element (if scrolling to a specific element)
   - Omit: text, seconds

4. **Wait Tool**:
   - Include: Tool, seconds
   - Omit: element, text, direction

5. **Go Back Tool**:
   - Include only: Tool
   - Omit all other fields

6. **Return to Google Tool**:
   - Include only: Tool
   - Omit all other fields

7. **Respond with Answer Tool**:
   - Include: Tool, text (containing the answer)
   - Omit: element, direction, seconds

## Planning Strategies

1. **Input-Driven Planning**: 
   - Ensure your plan directly addresses the task specified in the `input` parameter.
   - Use the information from `bbox_descriptions` and `img` to identify the most relevant elements for the task.

2. **Efficient Data Usage**: 
   - Only include data fields that are directly relevant to the tool being used.
   - Use the bbox_descriptions to accurately identify elements when needed.

3. **Clarity and Conciseness**:
   - Ensure each planned action is clear and contains only the essential information.
   - Avoid redundant or unnecessary details in your plan.

4. **Logical Sequences**: 
   - Group related actions together in your plan.
   - Ensure the order of actions is logical and efficient based on the webpage layout visible in the `img`.

5. **Handling Non-Annotated Elements**:
   - When planning interactions with elements not in `bbox_descriptions`, provide clear descriptions based on what you can see in the `img`.
   - If using the Click or Type tools for non-annotated elements, estimate positions based on their relation to annotated elements.

## Handling Edge Cases in Planning

1. **Ambiguous Situations**:
   - If the `bbox_descriptions` or `img` are unclear, plan multiple alternative actions.
   - Clearly explain the reasoning for each alternative in your plan.

2. **Missing Critical Elements**:
   - If elements crucial for the `input` task are not visible in `img` or described in `bbox_descriptions`, plan exploration actions (like scrolling).
   - Include alternative plans if critical elements might be missing.

3. **Error Scenarios**:
   - Plan for potential errors or unexpected outcomes based on what you can infer from the `img` and `bbox_descriptions`.
   - Include alternative actions in case primary actions might fail.

## Plan Reporting

1. **Success Criteria**:
   - Clearly define what constitutes successful completion of the task specified in the `input`.
   - Explain how your plan meets these criteria using the information from `img` and `bbox_descriptions`.

2. **Plan Summary**:
   - Conclude your plan with a concise summary of the planned actions and their expected outcomes.
   - Highlight any potential challenges or areas of uncertainty in your plan based on the provided input parameters.

## Ethical Considerations in Planning

1. Do not plan interactions with login forms or submissions of personal information, even if they appear in the `img` or `bbox_descriptions`.
2. Avoid planning interactions with potentially harmful or inappropriate content visible in the `img`.
3. Prioritize user safety and data protection in your planning, considering the nature of the `input` task.

Remember, your goal is to create efficient, clear plans for completing the web-based tasks specified in the `input`, using the information provided in `img` and `bbox_descriptions`. Focus on providing only the necessary details for each planned action, ensuring that your plan is both comprehensive and adaptable to various web scenarios.
"""


prompt = PromptTemplate(
    template=template,
    input_variables=["bbox_descriptions", "img", "input"],
    optional_variables=["scratchpad"],
)
from key import api_key
from langchain_openai import ChatOpenAI
from pydant import Plan, event

llm = ChatOpenAI(model = "gpt-4o-mini", api_key=api_key)

structured_llm = llm.with_structured_output(Plan)
planner = prompt | llm






















theme_prompt = """
# RCCG Event Information Search Prompt

Search for precise information about the following RCCG (Redeemed Christian Church of God) event:

Event Name
Starting Month

IMPORTANT: 
- Accuracy is determined by matching the event name and confirming that at least one event day falls within the specified month. 
- If the event spans multiple days, provide details for all days of the event, even if some days fall outside the starting month.
- Return the **exact date(s)** for each event day that falls within the specified month and any additional months.

Provide the following details ONLY if you are certain of their accuracy based on the event name and matching date(s), and return as JSON:

1. Theme: [Full theme of the event or N/A]
2. Date: [Exact date(s) of the event in YYYY/MM/DD format, based on the event span or N/A]
3. Time: [Specific time(s) of the event or N/A]
4. Venue: [Precise location of the event or N/A]
5. Additional Info: [Any other crucial details (e.g., speakers, registration) or N/A]

Instructions:
- Search for events where the event name matches exactly and at least one event day falls within the specified month.
- For multi-day events, automatically include all dates for the event, even if some dates fall in the following month. The tool will retrieve and handle this automatically.
- If exact date and time information for specific days is missing, assign the details from the event range to those specific days. This means if only the range is available, use those details for the corresponding days.
- Use "N/A" for any missing or unconfirmed information that cannot be inferred from the event range.

Source: [Include a direct link to the source that confirms the event name and date(s), or N/A if no such source is found]

Accuracy Notes:
- Accuracy is determined based on the event name match and the presence of at least one day of the event within the specified month. The tool should handle cases where the event spans multiple months, but only return exact dates within the confirmed span.
- If exact details are not available for specific days, utilize the general details from the event range for those days. Do not provide partial matches or similar event names. If there is uncertainty, mark fields as "N/A."
"""




url_prompt = '''
# RCCG Event YouTube URL Search Prompt

Search for the YouTube URL of the following RCCG (Redeemed Christian Church of God) event:

Event Name
Event Theme
Event Date

Instructions:
1. Search for a YouTube video that matches the given event details.
2. The video title or description should closely match the event name and/or theme.
3. Verify that the video upload date is consistent with the event date (it should be on or after the event date, but not too far after).
4. If multiple videos are found, prioritize the official RCCG YouTube channel or the most viewed relevant video.
5. Return the result as a JSON object with the following structure:
   {
     "youtube_url": "<full_youtube_url_or_NA>"
   }
6. If no matching video is found, use "N/A" as the value for "youtube_url".

Important Notes:
- Ensure the URL is a valid YouTube link (should start with https://www.youtube.com/ or https://youtu.be/).
- Do not include any explanations or additional text outside the JSON structure.
- The JSON object should be the only output.

Remember: Accuracy is crucial. It's better to return "N/A" than to provide an incorrect or unrelated video URL.
'''