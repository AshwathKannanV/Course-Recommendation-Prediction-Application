import streamlit as st
import pandas as pd
import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import backend as backend

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid import GridUpdateMode, DataReturnMode

# Basic webpage setups
st.set_page_config(
   page_title="Course Recommender System",
   layout="wide",
   initial_sidebar_state="expanded",
)


# ------- Functions ------
# Load datasets
@st._cache_data
def load_ratings():
    return backend.load_ratings()


@st._cache_data
def load_course_sims():
    return backend.load_course_sims()

@st._cache_data
def load_profile():
    return backend.load_profile()

def load_courses():
    return backend.load_courses()

@st._cache_data
def load_courses_genre():
    return backend.load_courses_genre()

@st._cache_data
def load_bow():
    return backend.load_bow()


# Initialize the app by first loading datasets
def init__recommender_app():

    with st.spinner('Loading datasets...'):
        ratings_df = load_ratings()
        sim_df = load_course_sims()
        course_df = load_courses()
        course_bow_df = load_bow()
        profile_df = load_profile()
        course_genre_df = load_courses_genre()

    # Select courses
    st.success('Datasets loaded successfully...')

    st.markdown("""---""")
    st.subheader("Select courses that you have audited or completed: ")

    # Build an interactive table for `course_df`
    gb = GridOptionsBuilder.from_dataframe(course_df)
    gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    gb.configure_side_bar()
    grid_options = gb.build()

    # Create a grid response
    response = AgGrid(
        course_df,
        gridOptions=grid_options,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=False,
    )

    results = pd.DataFrame(response["selected_rows"], columns=['COURSE_ID', 'TITLE', 'DESCRIPTION'])
    results = results[['COURSE_ID', 'TITLE']]
    st.subheader("Your courses: ")
    st.table(results)
    return results


def train(model_name, params):

    if model_name == backend.models[0]:
        # Start training course similarity model
        with st.spinner('Training...'):
            time.sleep(0.5)
            backend.train(model_name, params)
        st.success('Done!')
    # TODO: Add other model training code here
    elif model_name == backend.models[1]:
        with st.spinner('Training...'):
            time.sleep(0.5)
            backend.train(model_name, params)
        st.success('Done!')
    elif model_name == backend.models[2]:
        with st.spinner('Training...'):
            time.sleep(0.5)
            backend.train(model_name, params)
        st.success('Done!')

    else:
        pass


def predict(model_name, user_ids, params):
    res = None
    # Start making predictions based on model name, test user ids, and parameters
    with st.spinner('Generating course recommendations: '):
        time.sleep(0.5)
        res = backend.predict(model_name, user_ids, params)
    st.success('Recommendations generated!')
    return res


# ------ UI ------
# Sidebar
st.sidebar.title('Personalized Learning Recommender')
# Initialize the app
selected_courses_df = init__recommender_app()

# Model selection selectbox
st.sidebar.subheader('1. Select recommendation models')
model_selection = st.sidebar.selectbox(
    "Select model:",
    backend.models
)

# Hyper-parameters for each model
params = {}
st.sidebar.subheader('2. Tune Hyper-parameters: ')
# Course similarity model
if model_selection == backend.models[0]:
    # Add a slide bar for selecting top courses
    top_courses = st.sidebar.slider('Top courses',
                                    min_value=0, max_value=100,
                                    value=10, step=1)
    # Add a slide bar for choosing similarity threshold
    course_sim_threshold = st.sidebar.slider('Course Similarity Threshold %',
                                             min_value=0, max_value=100,
                                             value=50, step=10)
    params['top_courses'] = top_courses
    params['sim_threshold'] = course_sim_threshold
# TODO: Add hyper-parameters for other models
# User profile model
elif model_selection == backend.models[1]:
    profile_sim_threshold = st.sidebar.slider('User Profile Similarity Threshold %',
                                              min_value=0, max_value=50,
                                              value=30, step=5)
    temp_user = st.sidebar.text_input(label="Input the user_id")
    params['profile_sim_threshold'] = profile_sim_threshold
    params['user_id'] = temp_user

# Clustering model
elif model_selection == backend.models[2]:
    cluster_no = st.sidebar.slider('Number of Clusters',
                                   min_value=0, max_value=50,
                                   value=20, step=1)
    temp_user_two= st.sidebar.text_input(label="Input the user_id to find the other users in the cluster")
    params['cluster_no'] = cluster_no
    params['temp_user_two'] = temp_user_two
    pass


# Training
st.sidebar.subheader('3. Training: ')
training_button = st.sidebar.button("Train Model")
training_text = st.sidebar.text('')
# Start training process
if training_button:
    train(model_selection, params)


# Prediction
st.sidebar.subheader('4. Prediction')
# Start prediction process
pred_button = st.sidebar.button("Recommend New Courses")
# selected_courses_df.shape[0] > 0:
if pred_button and model_selection == backend.models[0]:
    # Create a new id for current user session
    new_id = backend.add_new_ratings(selected_courses_df['COURSE_ID'].values)
    user_ids = [new_id]
    res_df = predict(model_selection, user_ids, params)
    res_df = res_df[['COURSE_ID', 'SCORE']]
    course_df = load_courses()
    res_df = pd.merge(res_df, course_df, on=["COURSE_ID"]).drop('COURSE_ID', axis=1)
    st.table(res_df)
elif pred_button and model_selection == backend.models[1]:
    # type(temp_user) == str
    # st.text(temp_user)
    user_ids = [1502801,1609720,87799]
    res_df = predict(model_selection, user_ids, params)
    st.table(res_df)
# res_df = pd.merge(res_df, course_df, on=["COURSE_ID"]).drop('COURSE_ID', axis=1)
elif pred_button and model_selection == backend.models[2]:
    # type(temp_user) == str
    user_ids = [1502801,1609720,87799]
    # st.text(temp_user_two)
    try:
        res_df = predict(model_selection, user_ids, params)
        st.table(res_df)
    except:
        st.sidebar.text("Please input another user")

