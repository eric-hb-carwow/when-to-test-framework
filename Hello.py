import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches


if 'selections' not in st.session_state:
    st.session_state.selections = []

if 'checks' not in st.session_state:
    st.session_state.checks = 0

evidence_type = ['AB test',
                'Pre/post analysis',
                'Big analysis',
                'Survey results',
                'Small analysis',
                'User interviews',
                'Industry evidence',
                'Expert opinion'
                ]
type_lookup = {
    'AB test': 6,
    'Pre/post analysis': 4,
    'Big analysis': 4,
    'Survey results': 3,
    'Small analysis': 3,
    'User interviews': 2,
    'Industry evidence': 1,
    'Expert opinion': 1
}

# Confidence limits
conf_low = 4
conf_mid = 7
conf_high = 10
conf_max = 14
# Risk limits
risk_low = 5
risk_mid = 10
risk_high = 15
risk_max = 20

# Colours
colours = {
    'Optional': '#38c399ff',
    'Encouraged': '#2fa37fff',
    'Essential': '#1edce8ff'
}


# descriptions 
main_description = """
# When to test
First calculate your confidence, next calculate your risk, then see where you end up on the board. 

If you are in Essential, then let's build an AB test! If you're in optional or encouraged, the decision framework is in this notion doc to discuss with stakeholders and analytics.
"""
conf_description = """
# Confidence
To calculate your confidence, sum up your evidence. Choose the type of evidence you have and how aligned it is with your hypothesis. Once you've input those, press "Add" and your confidence score will go up.
"""

risk_description = """
# Risk
To calculate risk, first find the opportunity size (monthly traffic x conversion rate to revenue x average revenue). These are typically easy to find via amplitude, ask your local analyst for help if needed.

Next, find the monthly revenue for your country and vertical, if the change will be in DE leasing, for example, you would use overall DE GYC revenue for the last month. This can be found in this tableau dashbaord, ask your local analyst for help if needed.

Finally, input the change size.
"""

def make_plot(x, y):
    
    # Plot the point
    plt.figure(figsize=(6, 4))
    plt.xlabel('Risk')
    plt.ylabel('Confidence')

    # Set X and Y axis limits
    plt.xlim(0, 20)
    plt.ylim(0, 14)
    # Specify the new tick locations and labels
    x_ticks = [2.5, 7.5, 12.5, 17.5]  # Change these to your desired tick locations
    xtick_labels = ['V Low', 'Low', 'Mid', 'High']  # Change these to the labels you want
    y_ticks = [2, 5.5, 8.5, 12]  # Change these to your desired tick locations
    ytick_labels = ['Low', 'Mid', 'High', 'V High']  # Change these to the labels you want

    plt.xticks(x_ticks, xtick_labels)
    plt.yticks(y_ticks, ytick_labels)

    # Colours for the different areas
    encouraged = patches.Rectangle((0, 0), 30, 25, linewidth=0, facecolor=colours['Encouraged'])
    optional = patches.Polygon([[0, conf_mid], [risk_low, conf_mid], [risk_low, conf_high], [risk_mid, conf_high], [risk_mid, conf_max], [0, conf_max] ], closed=True, facecolor=colours['Optional'])
    essential = patches.Polygon([[risk_low, 0], [risk_low, conf_low], [risk_mid, conf_low], [risk_mid, conf_high], [risk_max, conf_high], [risk_max, 0] ], closed=True, facecolor=colours['Essential'])

    # Add the custom shape to the plot
    plt.gca().add_patch(encouraged)
    plt.gca().add_patch(optional)
    plt.gca().add_patch(essential)

    # Add vertical lines at X = 5, 10, and 25
    plt.axvline(x=risk_low, color='#f4f2f7', linestyle='--')
    plt.axvline(x=risk_mid, color='#f4f2f7', linestyle='--')
    plt.axvline(x=risk_high, color='#f4f2f7', linestyle='--')

    # Add horizontal lines at Y = 4, 7, and 10
    plt.axhline(y=conf_low, color='#f4f2f7', linestyle='--')
    plt.axhline(y=conf_mid, color='#f4f2f7', linestyle='--')
    plt.axhline(y=conf_high, color='#f4f2f7', linestyle='--')

    legend_handles = [
            patches.Patch(color=colours['Optional'], label='Optional'),
            patches.Patch(color=colours['Encouraged'], label='Encouraged'),
            patches.Patch(color=colours['Essential'], label='Essential')
        ]
    plt.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3,
               facecolor='none', edgecolor='none')



    plt.scatter(x, y, color='red', marker='o', s=200)

    # st.pyplot(plt)

    # check whether the point is in each area:
    essential_path = essential.get_path()
    optional_path = optional.get_path()

    # Check if the point lies within the polygon
    if essential_path.contains_point((x, y)):
        outcome = 'Essential'
    elif optional_path.contains_point((x, y)):
        outcome = 'Optional'
    else:
        outcome = 'Encouraged'

    return (plt, outcome)

def get_alignment(amount):
    if amount < -50:
        alignment = 'opposed to'
    elif amount < -10:
        alignment = 'slightly opposed to'
    elif amount < 50:
        alignment = 'neutral to'
    elif amount < 80:
        alignment = 'mostly aligns with'
    else:
        alignment = 'highly aligned with'
    return alignment

def get_confidence():
    type = st.radio('Type of evidence:', evidence_type)
    amount = st.slider('How aligned with the hypothesis is this evidence?',min_value=-100, max_value=100, value=100, step=20)
    st.caption(f'Evidence is **{get_alignment(amount)}** our hypothesis')
    age = st.slider('How many years ago is this evidence from?', min_value=0, max_value=6, step=1, value=0)
    st.caption('Older evidence gets fewer points')
    if age > 1:
        points_minus_age = type_lookup[type] - age + 1
        if points_minus_age < 0: 
            points_minus_age = 0
    else: 
        points_minus_age = type_lookup[type]
    if st.button('Add'):
        numeric_value = points_minus_age
        final_value = numeric_value * (amount) / 100
        st.session_state.selections.append((type, final_value, amount))
    total_confidence = 0
    
    for idx, (type_name, final_value, amount) in enumerate(st.session_state.selections, start=1):
        total_confidence += final_value
    
    if total_confidence <= 0:
        total_confidence = 0.01
    if total_confidence >= conf_max:
        total_confidence = conf_max - 0.01

    return total_confidence

def get_risk():
    opp_size = st.number_input('Enter the opportunity size: (monthly traffic * conversion rate to revenue * average revenue)')
    monthly_revenue = st.number_input('Enter the country & vertical monthly revenue')
    st.caption('To find revenue, see [this](https://10ay.online.tableau.com/#/site/carwowtest/views/MarketingDailyDashboard2_0/MarketingBusinessHealthDashboard) tableau dashboard')
    
    change_size = st.slider('How large is the change?', min_value=0, max_value=100, step=5)
    st.caption('Suggestion:  XS 5 | S 20 | M 50 | L 90 | XL 100')
    
    if monthly_revenue * opp_size * change_size == 0:
        risk = 0
        return {'risk': 0,
                'opportunity': 0, 
                'revenue': 0, 
                'change_size': 0}
    else:
        risk = opp_size / monthly_revenue * change_size
    if risk >= risk_max:
        risk = risk_max - .01
    if risk <= 0:
        risk = 0 + .01
    return {'risk': risk,
                'opportunity': opp_size, 
                'revenue': monthly_revenue, 
                'change_size': change_size}

def show_checkboxes():
    st.markdown('#### Tick relevant boxes below')
    option_1 = st.checkbox('Would a positive or negative result change a decision?')
    option_2 = st.checkbox('Will anyone want to know the impact?')
    option_3 = st.checkbox('Will learnings provide future value or influence future work?')
    option_4 = st.checkbox('Do we want to have accurate measurement?')
    option_5 = st.checkbox('Do we want to reduce risk further?')
    option_6 = st.checkbox('Is there low opportunity cost to setup a test?')
    st.session_state.checks = option_1 + option_2 + option_3 + option_4 + option_5 + option_6

def show_confidence(confidence):
    if confidence < conf_low:
            conf_cat = 'Low'
    elif conf_low <= confidence < conf_mid:
        conf_cat = 'Mid'
    elif conf_mid <= confidence < conf_high:
        conf_cat = 'High'
    else:
        conf_cat = 'V High'
    st.write(f'## Confidence: {conf_cat}')
    if not bool(st.session_state.selections):
        st.write('None')
    for index, (type_name, final_value, amount) in enumerate(st.session_state.selections):
        col1, col2 = st.columns([0.1, 0.9])
        if col1.button(f"x", key=f"delete_{index}"):
            del st.session_state.selections[index]
            st.experimental_rerun()
        
        alignment = get_alignment(amount)
        col2.write(f"{type_name} {alignment} our hypothesis")

def show_risk(risk_values):
    if risk_values['risk'] < risk_low:
        risk_cat = 'V Low'
    elif risk_low <= risk_values['risk'] < risk_mid:
        risk_cat = 'Low'
    elif risk_mid <= risk_values['risk'] <= risk_high:
        risk_cat = 'Mid'
    else:
        risk_cat = 'High'

    st.markdown(f'## Risk: {risk_cat}')
    st.caption(f'Opportunity: {risk_values["opportunity"]}  \n Monthly revenue: {risk_values["revenue"]}  \n Change size: {risk_values["change_size"]}')

def show_outcome(outcome):
    if outcome == 'Essential':
        st.write('## AB test!')

    elif outcome == 'Encouraged':
        if st.session_state.checks > 0:
            st.write('## AB test!')
        else: 
            st.write('## Measure but no AB test')
    
    else:
        if st.session_state.checks > 3:
            st.write('## AB test!')
        elif st.session_state.checks > 1:
            st.write('## Measure but no AB test')
        else:
            st.write('## Roll it out!')

def main():
    st.write(main_description)
    
    # User inputs for confidence and risk
    left_column, _, right_column = st.columns([1, 0.2, 1])
    with left_column:
        st.write(conf_description)
        confidence = get_confidence()

    with right_column:
        st.write(risk_description)
        risk_values = get_risk()

    st.write(' ')
    # Showing the user their inputs for confidence and risk
    left_column2, _, right_column2 = st.columns([1, 0.1, .8])
    with left_column2:
        show_confidence(confidence)
            
    with right_column2:
        show_risk(risk_values)

    # Showing the graph and outcome
    (plt, outcome) = make_plot(risk_values['risk'], confidence)

    
    checkbox_col, _, graph = st.columns([.8, .1, 1])

    with checkbox_col:
        show_checkboxes()

    with graph:
        st.markdown(f'### AB testing is <span style="color: {colours[outcome]};">{outcome}</span> → <ins>{show_outcome(outcome)}</ins>', unsafe_allow_html=True)
        st.pyplot(plt)

if __name__ == '__main__':
    main()
