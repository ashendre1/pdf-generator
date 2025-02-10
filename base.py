import dash
from dash import dcc, html, Output, Input, ctx
import pandas as pd
import plotly.express as px
import pdfkit
import base64
import dash.dash_table as dt

# Load Data from Local File
file_path = "C:\\Users\\Shendre\\Downloads\\Class Profile_DummyData - Sheet1.csv"  # Change to actual file path
df = pd.read_csv(file_path)

# Get unique courses
unique_courses = df["Class"].unique()

# Dash App
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Function to generate course dashboard
def generate_dashboard(course_name):
    course_df = df[df["Class"] == course_name].iloc[0]

    # Define table data
    table_data = [
        {"Category": "Prior-Term Course", "Course": course_df['Popular.Co-Requisite.Name.1'], "Students": course_df['Popular.Co-Requisite.Number.1']},
        {"Category": "Prior-Term Course", "Course": course_df['Popular.Co-Requisite.Name.2'], "Students": course_df['Popular.Co-Requisite.Number.2']},
        {"Category": "Concurrent Course", "Course": course_df['Popular.Pre-Requisite.Name.1'], "Students": course_df['Popular.Pre-Requisite.Number.1']},
        {"Category": "Concurrent Course", "Course": course_df['Popular.Pre-Requisite.Name.2'], "Students": course_df['Popular.Pre-Requisite.Number.2']},
    ]

    return html.Div([
        html.H1(f"Class: {course_df['Class']} - Section {course_df['Section']}"),
        html.H2(f"Semester: {course_df['Semester']} | Instructor: {course_df['Instructor']}"),
        html.H3(f"Average GPA: {course_df['Avg.GPA']}"),
        html.H3(f"Student Demographic"),
        # Wrap Pie Charts in a Flexbox Container
        html.Div([
            dcc.Graph(
                figure=px.pie(
                    names=["Female", "Male", "Other"],
                    values=[course_df["Enrollment.Women"], course_df["Enrollment.Male"],
                            course_df["Enrollment.OtherGender"]],
                    title="Gender",
                    color_discrete_sequence=["#005035", "#A49665", "#802F2D"]
                ),
                style={"width": "48%", "display": "inline-block"}
            ),
            dcc.Graph(
                figure=px.pie(
                    names=["In-State", "Out-of-State"],
                    values=[course_df["Enrollment.InState"], course_df["Enrollment.OutOfState"]],
                    title="Residency",
                    color_discrete_sequence=["#005035", "#A49665", "#007377"]
                ),
                style={"width": "48%", "display": "inline-block"}
            )
        ], style={"display": "flex", "justifyContent": "space-between"}),

        # Ethnicity Enrollment Bar Chart
        dcc.Graph(
            figure=px.bar(
                x=["White", "Asian", "Hispanic", "African American", "International", "Other"],
                y=[course_df["Enrollment.White"], course_df["Enrollment.Asian"], course_df["Enrollment.Hispanic"],
                   course_df["Enrollment.AfricanAmerican"], course_df["Enrollment.International"],
                   course_df["Enrollment.Other.Ethnicity"]],
                title="Ethnicity",
                labels={"x": "", "y": "Number of Students"},
                color=["White", "Asian", "Hispanic", "African American", "International", "Other"],
                color_discrete_sequence=["#005035", "#A49665", "#802F2D", "#007377", "#101820", "#899064"]
            )
        ),


        html.H3(f"Grade Distribution"),
        # Final Grades Bar Chart
        dcc.Graph(
            figure=px.bar(
                x=["A", "B", "C", "D", "F", "W"],
                y=[course_df["FinalGrade.A"], course_df["FinalGrade.B"], course_df["FinalGrade.C"],
                   course_df["FinalGrade.D"], course_df["FinalGrade.F"], course_df["FinalGrade.W"]],
                labels={"x": "Grade", "y": "Number of Students"},
                color=["A", "B", "C", "D", "F", "W"],
                color_discrete_sequence=["#005035", "#A49665", "#802F2D", "#007377", "#101820", "#899064"]
            )
        ),

        # Add the Table
        html.H3("Common Concurrent & Prior-Term Courses", style={"margin-top": "30px"}),
        dt.DataTable(
            columns=[
                {"name": "Category", "id": "Category"},
                {"name": "Course", "id": "Course"},
                {"name": "Students", "id": "Students"},
            ],
            data=table_data,
            style_table={"width": "60%", "margin": "auto"},  # Center table
            style_cell={"textAlign": "left", "padding": "10px"},
            style_header={"backgroundColor": "#f2f2f2", "fontWeight": "bold"},
            style_data_conditional=[
                {"if": {"column_id": "Category", "filter_query": '{Category} = ""'}, "color": "transparent"}
            ]
        )
    ])

# Layout
app.layout = html.Div([
    html.Div([
        html.H2("Course Selection"),
        dcc.Dropdown(
            id="course-dropdown",
            options=[{"label": course, "value": course} for course in unique_courses],
            value=unique_courses[0]  # Default selection
        )
    ], style={"width": "20%", "display": "inline-block", "verticalAlign": "top"}),

    html.Div(id="course-dashboard", style={"width": "75%", "display": "inline-block"}),

    # Download Button - Always Present
    html.Button("Download as PDF", id="download-pdf", n_clicks=0),

    # Hidden Download Component - Always Present
    dcc.Download(id="pdf-download")
])

# Function to convert charts to images for PDF
def get_image_from_figure(figure):
    img_bytes = figure.to_image(format="png")
    encoded_image = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:image/png;base64,{encoded_image}"

# Callback to update dashboard when course is selected
@app.callback(
    Output("course-dashboard", "children"),
    Input("course-dropdown", "value")
)
def update_dashboard(selected_course):
    return generate_dashboard(selected_course)


# Callback for PDF Download
@app.callback(
    Output("pdf-download", "data"),
    Input("download-pdf", "n_clicks"),
    Input("course-dropdown", "value"),
    prevent_initial_call=True
)
def generate_pdf(n_clicks, selected_course):
    if ctx.triggered_id != "download-pdf":
        return dash.no_update
    course_df = df[df["Class"] == selected_course].iloc[0]

    # Generate charts with increased text size
    gender_chart = px.pie(
        names=["Female", "Male", "Other"],
        values=[course_df["Enrollment.Women"], course_df["Enrollment.Male"], course_df["Enrollment.OtherGender"]],
        title="Gender",
        color_discrete_sequence=["#005035", "#A49665", "#802F2D"]
    )
    gender_chart.update_layout(
        title_font_size=30,  # Increase title size
        legend_font_size=25,  # Increase legend size
        font=dict(size=25)  # Increase general text size
    )

    residency_chart = px.pie(
        names=["In-State", "Out-of-State"],
        values=[course_df["Enrollment.InState"], course_df["Enrollment.OutOfState"]],
        title="Residency",
        color_discrete_sequence=["#005035", "#A49665", "#802F2D"]
    )
    residency_chart.update_layout(
        title_font_size=30,
        legend_font_size=25,
        font=dict(size=25)
    )

    ethnicity_chart = px.bar(
        x=["White", "Asian", "Hispanic", "African American", "International", "Other"],
        y=[course_df["Enrollment.White"], course_df["Enrollment.Asian"], course_df["Enrollment.Hispanic"],
           course_df["Enrollment.AfricanAmerican"], course_df["Enrollment.International"],
           course_df["Enrollment.Other.Ethnicity"]],
        title="Ethnicity",
        color=["White", "Asian", "Hispanic", "African American", "International", "Other"],
        color_discrete_sequence=["#005035", "#A49665", "#802F2D", "#007377", "#101820", "#899064"],
        labels={"x": "", "y": "Number of Students"}
    )

    ethnicity_chart.update_layout(
        title_font_size=25,
        legend_font_size=20,
        font=dict(size=20),
        showlegend=False
    )

    grades_chart = px.bar(
        x=["A", "B", "C", "D", "F", "W"],
        y=[course_df["FinalGrade.A"], course_df["FinalGrade.B"], course_df["FinalGrade.C"],
           course_df["FinalGrade.D"], course_df["FinalGrade.F"], course_df["FinalGrade.W"]],
        title="Grade Distribution",
        labels={"x": "Grade", "y": "Number of Students"},
        color=["A", "B", "C", "D", "F", "W"],
        color_discrete_sequence=["#005035", "#A49665", "#802F2D", "#007377", "#101820", "#899064"]
    )

    grades_chart.update_layout(
        title=dict(
            text="<b>Final Grades</b>",  # Makes the title bold using HTML tags
            font=dict(size=25)  # Increases the title font size
        ),
        legend=dict(font=dict(size=20)),  # Adjust legend font size
        font=dict(size=20),  # Adjust overall font size
        showlegend=False
    )

    table_data = [
        {"Category": "Prior-Term Course", "Course": course_df['Popular.Co-Requisite.Name.1'],
         "Students": course_df['Popular.Co-Requisite.Number.1']},
        {"Category": "Prior-Term Course", "Course": course_df['Popular.Co-Requisite.Name.2'],
         "Students": course_df['Popular.Co-Requisite.Number.2']},
        {"Category": "Concurrent Course", "Course": course_df['Popular.Pre-Requisite.Name.1'],
         "Students": course_df['Popular.Pre-Requisite.Number.1']},
        {"Category": "Concurrent Course", "Course": course_df['Popular.Pre-Requisite.Name.2'],
         "Students": course_df['Popular.Pre-Requisite.Number.2']},
    ]

    table_html = f"""
        <table border="1" cellpadding="5" cellspacing="0" style="width: 60%;text-align: left;">
            <thead>
                <tr style="background-color: #f2f2f2; font-weight: bold;">
                    <th>Category</th>
                    <th>Course</th>
                    <th>Students</th>
                </tr>
            </thead>
            <tbody>
                {"".join([
                    f"<tr><td>{row['Category']}</td><td>{row['Course']}</td><td>{row['Students']}</td></tr>"
                    for row in table_data if row['Course']
                ])}
            </tbody>
        </table>
        """

    # Convert figures to base64 images
    gender_chart_image = get_image_from_figure(gender_chart)
    residency_chart_image = get_image_from_figure(residency_chart)
    ethnicity_chart_image = get_image_from_figure(ethnicity_chart)
    grades_chart_image = get_image_from_figure(grades_chart)

    # HTML Content for PDF
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
            }}
            .chart-table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .chart-table td {{
                width: 50%;
                text-align: center;
            }}
            .chart-table img {{
                width: 90%;
            }}
        </style>
    </head>
    <body>
        <h1>Class: {course_df['Class']} - Section {course_df['Section']}</h1>
        <h2>Semester: {course_df['Semester']} | Instructor: {course_df['Instructor']}</h2>
        <h3>Average GPA: {course_df['Avg.GPA']}</h3>

        <h3>Student Demographics</h3>

        <!-- Pie Charts Side by Side using Table -->
        <table class="chart-table">
            <tr>
                <td>
                    <img src="{gender_chart_image}" />
                </td>
                <td>
                    <img src="{residency_chart_image}" />
                </td>
            </tr>
        </table>

        <img src="{ethnicity_chart_image}" width="600" style="padding-top: 75px;"/>
        
        <img src="{grades_chart_image}" width="600" style="padding-bottom: 75px;"/>
        
        <h3>Common Concurrent & Prior-Term Courses</h3>
        {table_html}

    </body>
    </html>"""


    pdf_path = f"{selected_course}_report.pdf"

    # Convert HTML to PDF
    try:
        config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        pdfkit.from_string(html_content, pdf_path, configuration=config)
    except OSError:
        pdfkit.from_string(html_content, pdf_path)

    return dcc.send_file(pdf_path)

# Run App
if __name__ == '__main__':
    app.run_server(debug=True)
