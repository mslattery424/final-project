"""
Madison Slattery
CS230 - SN5
Data - New York City Vehicle Collisions

This program allows users to interact with and select specific parts of data to display. User inputs are contained in a
sidebar and include radio buttons to select a color scheme for graphs, start and end date selection to choose between
which dates the data will appear from, a checkbox to display the dataframe, and a button to display everything.
"""

import pandas as pd
import streamlit as st
from PIL import Image
import altair as alt
import pydeck as pdk
import mapbox as mb


def open_file(filename="nyc_veh_crash_sample.csv"):
    df = pd.read_csv(filename)
    return df


df = open_file()

# changing column headings to lowercase using a list comprehension
df.columns = [x.lower() for x in df.columns]

# removing rows where there is not a value for latitude
df = df[df["latitude"].notna()]
df = df[df["borough"].notna()]

# changing latitude and longitude from strings to floats
df["latitude"] = pd.to_numeric(df["latitude"], downcast="float")
df["longitude"] = pd.to_numeric(df["longitude"], downcast="float")

# changing from strings to dates
df['date'] = pd.to_datetime(df['date'])

# dropping columns that are not needed
df.drop(["on street name", "cross street name", "off street name", "vehicle 1 type", "vehicle 2 type",
         "vehicle 3 type", "vehicle 4 type", "vehicle 5 type", "vehicle 1 factor", "vehicle 2 factor",
         "vehicle 3 factor", "vehicle 4 factor", "vehicle 5 factor"], inplace=True, axis=1)


def data_inputs(start_date, last_date):
    start = st.sidebar.date_input('Start Date', start_date)
    end = st.sidebar.date_input('End Date', last_date)

    options = st.sidebar.selectbox("Injury/Mortality Rate for Graph 3",
                                   ('persons injured', 'persons killed', 'pedestrians injured',
                                    'pedestrians killed', 'cyclists injured', 'cyclists killed',
                                    'motorists injured', 'motorists killed'))

    checkbox = st.sidebar.checkbox("Display DataFrame")
    button = st.sidebar.button('Get Charts')

    return start, end, options, checkbox, button


def color_inputs():
    color_radio = st.sidebar.radio("Select a color scheme for graphs:", ("Blue", "Green", "Magenta", "Orange", "Red"))
    if color_radio == "Blue":
        color_input = "blue"
        color1 = "blue"
        color2 = "green"
    elif color_radio == "Green":
        color_input = "green"
        color1 = "green"
        color2 = "yellow"
    elif color_radio == "Magenta":
        color_input = "magenta"
        color1 = "blue"
        color2 = "red"
    elif color_radio == "Orange":
        color_input = "orange"
        color1 = "red"
        color2 = "yellow"
    else:
        color_input = "red"
        color1 = "red"
        color2 = "orange"

    return color_input, color1, color2


def main():
    st.title("New York City")
    image = Image.open('nyc-skyline.jpg')
    st.image(image, caption='Image Source: https://www.cynopsis.com/nyc-skyline/')

    st.sidebar.header("Data Inputs")
    color_input, color1, color2 = color_inputs()
    start, end, options, checkbox, button = data_inputs(pd.to_datetime("2015-01-01"), pd.to_datetime("2017-02-28"))

    if checkbox:
        st.header("NYC Car Accident DataFrame")
        st.write(df)

    if button:
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)
        df.drop(df[df['date'] < start].index, inplace=True)  # dropping date values outside user input date range
        df.drop(df[df['date'] > end].index, inplace=True)

        st.header("Car Accident Locations")  # map of where each accident from dataset occurred
        st.map(df)  # I tried to make this map customizable but when I used the code that is commented out below,
        # I received an error message that said "TypeError: vars() argument must have __dict__ attribute"
        # I gave this multiple attempts following both Prof. Frydenberg's code as well as the code in
        # both pydek and streamlit's documentations. I wanted to leave this code commented out in case
        # you wanted to take a look and/or could figure out why it was not working

        # view_state = pdk.ViewState(
        #     latitude=df["latitude"].mean(),
        #     longitude=df["longitude"].mean(),
        #     zoom=11,
        #     pitch=0.5,
        # )
        # layer1 = pdk.Layer(
        #     'ScatterplotLayer',
        #     data=df,
        #     get_position='[longitude, latitude]',
        #     get_color=[0, 0, 255],
        #     get_radius=200,
        #     pickable=True,
        # )
        #
        # tool_tip = {"html": "date:<br/> <b>{date}</b> ",
        #             "style": {"backgroundColor": "steelblue",
        #                       "color": "white"}
        #             }
        #
        # map1 = pdk.Deck(
        #     map_style='mapbox://styles/mapbox/light-v9',
        #     initial_view_state=view_state,
        #     layers= layer1,
        #     # mapbox_key=MAPBOX_API_KEY,
        #     tooltip=tool_tip
        # )
        #
        # st.pydeck_chart(map1)

        st.header("Car Accidents per Day")  # line chart of car accidents per day

        line_data = df["date"].value_counts()
        ld = pd.DataFrame(line_data)  # creating a dataframe of the dates and their counts
        ld = ld.reset_index()
        ld.columns = ['Date', 'Number of Accidents']
        b = alt.Chart(ld).mark_line().encode(
            x='Date',
            y='Number of Accidents',
            color=alt.value(color_input),
            tooltip=['Date', 'Number of Accidents']
        ).properties(
            width=800,
            height=500)
        st.altair_chart(b)

        st.header(
            "Injury/Mortality Chart")  # bubble chart of number of injuries/deaths per day by borough based on user input
        c = alt.Chart(df).mark_circle().encode(
            x='borough',
            y='date',
            size=options,
            color=alt.Color(options,
                            scale=alt.Scale(
                                range=[color1, color2]),
                            ),
            tooltip=['date', 'borough', options]
        ).properties(
            width=800,
            height=500)

        st.altair_chart(c)

        stat_dict = {
            "max": df[options].max(), "min": df[options].min(), "mean": df[options].mean()
        }

        st.header("Quick Statistics")
        st.write(
            f"The maximum number of {options} from {start.strftime('%x')} to {end.strftime('%x')} is {stat_dict['max']}.",
            f"The minimum is {stat_dict['min']}.",
            f"The average is {stat_dict['mean']}.")


main()
