import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches


if 'selections' not in st.session_state:
    st.session_state.selections = []

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

    st.pyplot(plt)

    # check whether the point is in each area:
    essential_path = essential.get_path()
    optional_path = optional.get_path()

    # Check if the point lies within the polygon
    if essential_path.contains_point((x, y)):
        return 'Essential'
    elif optional_path.contains_point((x, y)):
        return 'Optional'
    else:
        return 'Encouraged'

def get_confidence():

    type = st.radio('Type of evidence:', evidence_type)
    amount = st.slider('How aligned with the hypothesis is this evidence?',min_value=-100, max_value=100, value=100, step=20)
    st.caption('If the evidence fully supports your hypothesis, give it a 100, if it shows some support but there are questions, use 50. If it goes against your hypothesis, use negative numbers.')
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
        
    return total_confidence

def get_risk():
    opp_size = st.number_input('Enter the opportunity size: (monthly traffic * conversion rate to revenue * average revenue)')
    monthly_revenue = st.number_input('Enter the country & vertical monthly revenue')
    st.caption('To find revenue, see [this](https://10ay.online.tableau.com/#/site/carwowtest/views/MarketingDailyDashboard2_0/MarketingBusinessHealthDashboard) tableau dashboard')
    
    change_size = st.slider('How large is the change?', min_value=0, max_value=100)
    st.caption('Suggestion:  XS 5 | S 20 | M 50 | L 90 | XL 100')
    
    if monthly_revenue == 0:
        return {'opportunity': 0, 
                'revenue': 0, 
                'change_size': 0}
    else:
        return {'opportunity': opp_size, 
                'revenue': monthly_revenue, 
                'change_size': change_size}

def main():
    st.write("""
    # When to test
    First calculate your confidence, next calculate your risk, then see where you end up on the board. 

    If you are in Essential, then let's build an AB test! If you're in optional or encouraged, the decision framework is in this notion doc to discuss with stakeholders and analytics.
    """)

    left_column, _, right_column = st.columns([1, 0.2, 1])
    with left_column:
        st.write("""
        # Confidence
        To calculate your confidence, sum up your evidence. Choose the type of evidence you have and how aligned it is with your hypothesis. Once you've input those, press "Add" and your confidence score will go up.
        """)
        confidence = get_confidence()
        if confidence <= 0:
            confidence = 0.01
        if confidence >= conf_max:
            confidence = conf_max - 0.01
    with right_column:
        st.write("""
        # Risk
        To calculate risk, first find the opportunity size (monthly traffic x conversion rate to revenue x average revenue). These are typically easy to find via amplitude, ask your local analyst for help if needed.

        Next, find the monthly revenue for your country and vertical, if the change will be in DE leasing, for example, you would use overall DE GYC revenue for the last month. This can be found in this tableau dashbaord, ask your local analyst for help if needed.

        Finally, input the change size.
        """)
         
        risk_values = get_risk()
        if risk_values['change_size'] == 0:
            risk = 0
        else:
            risk = risk_values['opportunity'] / risk_values['revenue'] * risk_values['change_size']
        if risk >= risk_max:
            risk = risk_max - .01
        if risk <= 0:
            risk = 0 + .01
    st.write(' ')
    
    left_column2, _, right_column2 = st.columns([1, 0.2, 1])
    with left_column2:
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
        for (type_name, final_value, amount) in st.session_state.selections:
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
            st.write(f"{type_name} {alignment} our hypothesis")
    
    with right_column2:
        if risk < risk_low:
            risk_cat = 'V Low'
        elif risk_low <= risk < risk_mid:
            risk_cat = 'Low'
        elif risk_mid <= risk <= risk_high:
            risk_cat = 'Mid'
        else:
            risk_cat = 'High'

        st.write(f'## Risk: {risk_cat}')
        st.write(f'Opportunity: {risk_values["opportunity"]}')
        st.write(f'Monthly revenue: {risk_values["revenue"]}')
        st.write(f'Change size: {risk_values["change_size"]}')
    
    st.write(' ')
    _, graph, _ = st.columns([.2, 1, .5])
    with graph:
        outcome = make_plot(risk, confidence)
    st.markdown(f'# AB testing is <span style="color: {colours[outcome]};">{outcome}</span>', unsafe_allow_html=True)

    if outcome != 'Essential':
        st.write('Please check the boxes below that are relevant for your change')
        option_1 = st.checkbox('Would a positive or negative result change a decision?')
        option_2 = st.checkbox('Will anyone want to know the impact?')
        option_3 = st.checkbox('Will learnings provide future value or influence future work?')
        option_4 = st.checkbox('Do we want to have accurate measurement?')
        option_5 = st.checkbox('Do we want to reduce risk further?')
        option_6 = st.checkbox('Is there low opportunity cost to setup a test?')
        a = option_1 + option_2 + option_3 + option_4 + option_5 + option_6
        
        if outcome == 'Encouraged':
            if a > 0:
                st.write('# AB test!')
            else: 
                st.write('# Measure impact without an AB test')
        
        if outcome == 'Optional':
            if a > 3:
                st.write('# AB test!')
            elif a > 1:
                st.write('# Measure impact without an AB test')
            else:
                st.write('# Let it roll without measurement')
        
        

if __name__ == '__main__':
    main()
