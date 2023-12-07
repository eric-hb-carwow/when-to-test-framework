import streamlit as st
import matplotlib.pyplot as plt

def main():
    st.title('Simple Scatter Plot App')
    
    # Get user inputs
    x = st.number_input('Enter X coordinate:', value=0)
    y = st.number_input('Enter Y coordinate:', value=0)
    
    # Display the input values
    st.write('Entered Coordinates:', (x, y))
    
    # Plot the point
    plt.figure(figsize=(6, 4))
    plt.scatter(x, y, color='red', marker='o')
    plt.title('Scatter Plot')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')

    # Set X and Y axis limits
    plt.xlim(0, 10)
    plt.ylim(0, 10)

    st.pyplot(plt)

if __name__ == '__main__':
    main()
