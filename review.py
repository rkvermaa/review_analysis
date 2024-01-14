import pandas as pd
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2

df = pd.read_excel("Product review.xlsx")
df = df[['Review']]
df.columns = ['review']
sample_reviews = str(df['review'][10:20])

prompt = '''
Tasks:
generate the summay of below reviews.
mention how many are positive, negative and neutral reviews along with its top 5 key words.
menation the top 5 topic all reviews are talking about

Instruction:
Give me output in python dictionary like this

Answer : {'summary':'[output]' , 'positive_review_count': "[output]", "top 5 positive key words":"[output]",
 'negative_review_count': "[output]", "top 5 negative key words":"[output]",
 "top 5 topic": "[output]"}
 Only give me above said answer dictionary
'''

final_prompt = prompt + ":\n" + sample_reviews


######################################################################################################
# In this section, we set the user authentication, user and app ID, model details, and the URL of
# the text we want as an input. Change these strings to run your own example.
######################################################################################################

# Your PAT (Personal Access Token) can be found in the portal under Authentification
PAT = '54a0ed80ce094bfca2cd6d53a51911c0'
# Specify the correct user_id/app_id pairings
# Since you're making inferences outside your app's scope
USER_ID = 'meta'
APP_ID = 'Llama-2'
# Change these to whatever model and text URL you want to use
MODEL_ID = 'llama2-70b-chat'
MODEL_VERSION_ID = 'acba9c1995f8462390d7cb77d482810b'
RAW_TEXT = final_prompt
# TEXT_FILE_URL = 'https://samples.clarifai.com/negative_sentence_12.txt'
# Or, to use a local text file, assign the url variable
# TEXT_FILE_LOCATION = 'YOUR_TEXT_FILE_LOCATION_HERE'

############################################################################
# YOU DO NOT NEED TO CHANGE ANYTHING BELOW THIS LINE TO RUN THIS EXAMPLE
############################################################################



channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)

metadata = (('authorization', 'Key ' + PAT),)

userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

# To use a local text file, uncomment the following lines
# with open(TEXT_FILE_LOCATION, "rb") as f:
#    file_bytes = f.read()

post_model_outputs_response = stub.PostModelOutputs(
    service_pb2.PostModelOutputsRequest(
        user_app_id=userDataObject,  # The userDataObject is created in the overview and is required when using a PAT
        model_id=MODEL_ID,
        version_id=MODEL_VERSION_ID,  # This is optional. Defaults to the latest model version
        inputs=[
            resources_pb2.Input(
                data=resources_pb2.Data(
                    text=resources_pb2.Text(
                        raw=RAW_TEXT
                        # url=TEXT_FILE_URL
                        # raw=file_bytes
                    )
                )
            )
        ]
    ),
    metadata=metadata
)
if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
    print(post_model_outputs_response.status)
    raise Exception(f"Post model outputs failed, status: {post_model_outputs_response.status.description}")

# Since we have one input, one output will exist here
output = post_model_outputs_response.outputs[0]

print("Completion:\n")
print(output.data.text.raw)

# Access the 'data' field and extract the 'text' field
data = output.data
text = data.text

# Access the 'raw' field inside 'text' to get the 'summary' dictionary
summary_dictionary = text.raw

start_index = summary_dictionary.find("{")  # Find the index of '{'
end_index = summary_dictionary.rfind("}")  # Find the index of '}' from the end

if start_index != -1 and end_index != -1:
    summary_dict_str = summary_dictionary[start_index:end_index + 1]  # Extract the substring containing the dictionary
    print(summary_dict_str)
    
import ast
summary_dict = ast.literal_eval(summary_dict_str)

print(summary_dict)