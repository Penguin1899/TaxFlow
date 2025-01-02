import time
from datetime import datetime
import streamlit as st
import pandas

st.title("Tax Tracker")
tab1, tab2, tab3 = st.tabs(["Calculate Tax", "Histortical Records", "Explore"])

months = [
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
    "January",
    "February",
    "March" 
]

incomes = {
    "fixed_income": {},
    "variable_income": {},
    "perquisite_income": {},
    "stcg": 0,
    "ltcg": 0,
    "interest_earned": 0
}


# Define the tax slabs for the new regime
new_regime_tax_slabs = [
    {"slab": "Up to ₹3,00,000", "start": 0, "end": 300000, "tax_rate": "0"},
    {"slab": "₹3,00,001 - ₹7,00,000", "start": 300001, "end": 700000, "tax_rate": "5"},
    {"slab": "₹7,00,001 - ₹10,00,000", "start": 700001, "end": 1000000, "tax_rate": "10"},
    {"slab": "₹10,00,001 - ₹12,00,000", "start": 1000001, "end": 1200000, "tax_rate": "15"},
    {"slab": "₹12,00,001 - ₹15,00,000", "start": 1200001, "end": 1500000, "tax_rate": "20"},
    {"slab": "Above ₹15,00,000", "start": 1500000, "end": "no_limit", "tax_rate": "30"}
]

# Define the tax slabs for the old regime
old_regime_tax_slabs = [
    {"slab": "Up to ₹3,00,000", "start": 0, "end": 300000, "tax_rate": "0"},
    {"slab": "₹3,00,001 - ₹7,00,000", "start": 300001, "end": 700000, "tax_rate": "5"},
    {"slab": "₹7,00,001 - ₹10,00,000", "start": 700001, "end": 1000000, "tax_rate": "10"},
    {"slab": "₹10,00,001 - ₹12,00,000", "start": 1000001, "end": 1200000, "tax_rate": "15"},
    {"slab": "₹12,00,001 - ₹15,00,000", "start": 1200001, "end": 1500000, "tax_rate": "20"},
    {"slab": "Above ₹15,00,000", "start": 1500000, "end": "no_limit", "tax_rate": "30"}
]

# slab display column config
slab_display_column_config = {
    "start": None,
    "end": None
}

# wrapper dict
tax_slabs = {
    "new_regime": new_regime_tax_slabs,
    "old_regime": old_regime_tax_slabs,
}

# placeholders
income_display_table = {}
dedutions_display_table = {}
tax_display_table = {}

# declare deductions
standard_deduction = 0
employee_pf_deduction = 0

# helper function
def calculate_total_tax_for_income_under_slabs(regime_chosen="", total_income_under_slabs=0):
    total_slab_tax_to_be_paid = 0
    for tax_slab in tax_slabs[regime_chosen]:

        set_break = False

        if tax_slab["end"] == "no_limit":
            taxable_income_in_current_range = total_income_under_slabs - int(tax_slab["start"])
        elif total_income_under_slabs > int(tax_slab["end"]):
            taxable_income_in_current_range = int(tax_slab["end"]) - int(tax_slab["start"])
        elif total_income_under_slabs < int(tax_slab["end"]):
            taxable_income_in_current_range = total_income_under_slabs - int(tax_slab["start"])
            set_break = True

        tax_in_range = (
            taxable_income_in_current_range * int(tax_slab["tax_rate"])
        ) / 100
        total_slab_tax_to_be_paid += tax_in_range
        
        if set_break:
            break
    
    return total_slab_tax_to_be_paid

# ---------------------
# streamlit app layout
# ---------------------
# tab to calculate taxes
with tab1:
    st.subheader("Calculate monthly and total taxes to be paid")

    # container to enter fiscal year and assessment year
    with st.container(border=True):
        st.caption("- **Enter basic details**")
        with st.expander("- General Info"):
            current_year = datetime.now().year
            next_year = current_year + 1
            upcoming_year = next_year + 1
            default_fy = f"{current_year}-{str(next_year)[2:]}"
            default_ay = f"{next_year}-{str(upcoming_year)[2:]}"

            fy = st.text_input("Enter FY for the tax filing", value=default_fy)
            ay = st.text_input("Enter AY for the tax filing", value=default_ay)
            tag = st.text_input("Enter a tag for saving this record", value=fy)

    # container to enter tax rates and other details
    with st.container(border=True):
        st.caption("- **Enter tax rates**")
        
        # default
        regime_chosen = "new_regime"

        # pick regime
        col1, col2 = st.columns(2)
        with col1:
            new_regime = st.checkbox("New Regime")
        with col2:
            old_regime = st.checkbox("Old Regime")
        
        # validation of regimes
        if new_regime and old_regime:
            st.error("Choose only one among old and new regimes...")
        elif new_regime:
            regime_chosen = "new_regime"
            st.info("Selected New Regime for taxation")
            with st.expander("View the tax-slab?"):
                # Create a Streamlit table
                df = st.dataframe(new_regime_tax_slabs, hide_index=True, use_container_width=True, column_config=slab_display_column_config)

                # Add a disclaimer
                st.caption(
                    "**Disclaimer:** This table provides a general overview. "
                    "Please consult with a qualified tax professional for personalized advice."
                )
        elif old_regime:
            regime_chosen = "old_regime"
            st.info("Selected Old Regime for taxation")
            with st.expander("View the tax-slab?"):
                # Create a Streamlit table
                df = st.dataframe(old_regime_tax_slabs, hide_index=True, use_container_width=True, column_config=slab_display_column_config)

                # Add a disclaimer
                st.caption(
                    "**Disclaimer:** This table provides a general overview. "
                    "Please consult with a qualified tax professional for personalized advice."
                )
        
        # select perquiste gain tax rate
        perquisite_gain_tax_rate = st.slider("Perquisite gain tax rate", min_value=0.0, max_value=55.0, value=30.0, step=0.5)
        # select perquiste gain tax rate
        stcg_tax_rate = st.slider("STCG tax rate", min_value=0.0, max_value=55.0, value=20.0, step=0.5)
        # select perquiste gain tax rate
        ltcg_tax_rate = st.slider("LTCG tax rate", min_value=0.0, max_value=55.0, value=12.5, step=0.5)

    # container for entering income details
    with st.container(border=True):

        st.caption("- **Enter details of incomes**")

        # get the incomes via columns
        col1, col2, col3 = st.columns(3)
        # for fixed salary
        with col1:
            with st.expander("Fill out monthly fixed income (salary)"):
                for month in months:
                    text_input = st.text_input(
                        f"{month}",
                        key=f"{month}'s fixed income"
                    )
                    incomes["fixed_income"][month] = int(text_input) if text_input.isdigit() else 0

        # for variable income
        with col2:
            with st.expander("Fill out monthly variable income (bonus etc)"):
                for month in months:
                    text_input = st.text_input(
                        f"{month}",
                        key=f"{month}'s variable income"
                    )
                    incomes["variable_income"][month] = int(text_input) if text_input.isdigit() else 0

        # for perquisite gains
        with col3:
            with st.expander("Fill out perquisite gains (RSUs, ESOP/ESPP etc)"):
                for month in months:
                    text_input = st.text_input(
                        f"{month}",
                        key=f"{month}'s perquisite income"
                    )
                    incomes["perquisite_income"][month] = int(text_input) if text_input.isdigit() else 0

        # for entering captial gains
        with st.expander("Fill out STCG / LTCG"):
            col1, col2 = st.columns(2)
            with col1:
                a = st.text_input("Total STCG")
                incomes["stcg"] = int(a) if a.isdigit() else 0
            with col2:
                a = st.text_input("Total LTCG")
                incomes["ltcg"] = int(a) if a.isdigit() else 0
        
        # for entering interest rates
        with st.expander("Fill out interest incomes"):
            col1, = st.columns(1)
            with col1:
                a = st.text_input("Total interest income")
                incomes["interest_earned"] = int(a) if a.isdigit() else 0
    
    # container for entering any deductions
    with st.container(border=True):
        st.caption("- **Enter deductions**")
        with st.expander("View details of deductions"):
            if new_regime and old_regime:
                st.error("Choose only one among old and new regimes...")
            elif new_regime:
                st.write(f"Standard deduction = Rs.75,000")
                standard_deduction=75000
            elif old_regime:
                st.write(f"Standard deduction = Rs.50,000")
                standard_deduction=75000
            st.write(f"Employee contribution to PF = Rs.21,600")
            employee_pf_deduction=21600
            
    # container for final calculation
    with st.container():
        if st.button("Calculate"):
            total_fixed_income = sum(list(incomes["fixed_income"].values())) if sum(list(incomes["fixed_income"].values())) else 0
            total_variable_income = sum(list(incomes["variable_income"].values())) if sum(list(incomes["variable_income"].values())) else 0
            total_perquisite_income = sum(list(incomes["perquisite_income"].values())) if sum(list(incomes["perquisite_income"].values())) else 0

            total_slab_income = total_fixed_income + total_variable_income + incomes["interest_earned"]
            total = incomes["stcg"] + incomes["ltcg"]  + total_perquisite_income + total_slab_income
            
            total_deductions = standard_deduction + employee_pf_deduction

            stcg_tax = incomes["stcg"] * (stcg_tax_rate/100)
            ltcg_tax = incomes["ltcg"] * (ltcg_tax_rate/100)
            total_perquisite_tax = total_perquisite_income  * (perquisite_gain_tax_rate/100) 
            total_slab_tax = calculate_total_tax_for_income_under_slabs(regime_chosen="new_regime", total_income_under_slabs=total_slab_income)
            tax_on_interest_earned = (incomes["interest_earned"]/total_slab_income) * total_slab_tax
            tax_on_capital_gains = f"{stcg_tax+ltcg_tax:.2f}"

            # formulate dataframe
            income_display_table = {
                "Total Fixed Salary": f"{total_fixed_income}",
                "Total Variable Pay": f"{total_variable_income}",
                "Total Perquisite Gain": f"{total_perquisite_income}",
                "Total Income under slabs": f"{total_slab_income}",
                "Gross (total) income": f"{total}"
            }

            dedutions_display_table = {
                "Employee PF Deduction": f"{employee_pf_deduction}",
                "Standard Deduction": f"{standard_deduction}", 
                "Total Deduction": f"{total_deductions}"
            }

            tax_display_table = {
                "Total slab tax": f"{total_slab_tax:.2f}",
                "Total perquisite gain tax": f"{total_perquisite_tax:.2f}",
                "Total STCG tax": f"{stcg_tax:.2f}",
                "Total LTCG tax": f"{ltcg_tax:.2f}",
            }

            advance_tax_display_table = {
                "Total advance tax - capital gains": f"{stcg_tax+ltcg_tax:.2f}",
                "Total advance tax - interest earned": f"{tax_on_interest_earned:.2f}",
                "Total advance tax": f"{stcg_tax+ltcg_tax+tax_on_interest_earned:.2f}"
            }
            # display total incomes/ deductions
            col1, col2 = st.columns([1,1], border=False, vertical_alignment="top")
            with st.spinner('Calculating...'):
                with col1:
                    df = pandas.DataFrame(income_display_table.items(), columns=["Income", "Value"])
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    # st.markdown(f":blue[Total income which can be taxed as per slabs (before deductions)] = `Rs.{total_slab_income}`")
                with col2:
                    df = pandas.DataFrame(dedutions_display_table.items(), columns=["Deductions", "Value"])
                    st.dataframe(df, use_container_width=True, hide_index=True)
            
            # display total taxes
            col1, = st.columns(1)
            with col1:
                df = pandas.DataFrame(tax_display_table.items(), columns=["Tax", "Value"])
                st.dataframe(df, use_container_width=True, hide_index=True)
            col1, = st.columns(1)
            with col1:
                df = pandas.DataFrame(advance_tax_display_table.items(), columns=["Advance Tax", "Value"])
                st.dataframe(df, use_container_width=True, hide_index=True)
    
# tab to display historical tax paid records
with tab2:
    st.subheader("Historical tax paid records")

# for future additon to explore latest tax news
with tab3:
    st.subheader("Explore")
    st.write("To implement....")