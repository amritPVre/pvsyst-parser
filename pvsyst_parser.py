import streamlit as st
import pandas as pd
import io

def parse_inverter_data(raw_data):
    """Parse single inverter data string and return required specifications."""
    try:
        fields = raw_data.split(';')
        
        # Helper function to clean and convert frequency string
        def parse_frequency(freq_str):
            if not freq_str:
                return 0
            freq_str = freq_str.strip().lower()
            if '50/60' in freq_str:
                return 50  # Return primary frequency
            try:
                # Remove 'hz' and convert to float
                return float(freq_str.replace('hz', '').strip())
            except:
                return 0

        # Define dictionary with correct field mappings according to sequence numbers from table
        inverter_specs = {
            'Manufacturer': str(fields[1]).strip() if len(fields) > 1 else "",  # Seq 1
            'Model': str(fields[2]).strip() if len(fields) > 2 else "",  # Seq 2
            'File_Name': str(fields[3]).strip() if len(fields) > 3 else "",  # Seq 3
            'Data_Source': str(fields[4]).strip() if len(fields) > 4 else "",  # Seq 4
            'Nominal_AC_Power_kW': float(fields[7]) if len(fields) > 7 and fields[7] and fields[7].strip() else 0,  # Seq 7
            'Maximum_AC_Power_kW': float(fields[8]) if len(fields) > 8 and fields[8] and fields[8].strip() else 0,  # Seq 8
            'Nominal_AC_current_A': float(fields[9]) if len(fields) > 9 and fields[9] and fields[9].strip() else 0,  # Seq 9
            'Maximum_AC_current_A': float(fields[10]) if len(fields) > 10 and fields[10] and fields[10].strip() else 0,  # Seq 10
            'Nominal_AC_Voltage_V': float(fields[11]) if len(fields) > 11 and fields[11] and fields[11].strip() else 0,  # Seq 11
            'Phase': str(fields[12]).strip() if len(fields) > 12 else "",  # Seq 12
            'Frequency_Hz': parse_frequency(fields[13]) if len(fields) > 13 else 0,  # Seq 13
            'Power_threshold_W': float(fields[17]) if len(fields) > 17 and fields[17] and fields[17].strip() else 0,  # Seq 17
            'Nominal_MPP_Voltage_V': float(fields[18]) if len(fields) > 18 and fields[18] and fields[18].strip() else 0,  # Seq 18
            'Min_MPP_Voltage_V': float(fields[19]) if len(fields) > 19 and fields[19] and fields[19].strip() else 0,  # Seq 19
            'Max_DC_Voltage_V': float(fields[20]) if len(fields) > 20 and fields[20] and fields[20].strip() else 0,  # Seq 20
            'Max_DC_Current_A': float(fields[24]) if len(fields) > 24 and fields[24] and fields[24].strip() else 0,  # Seq 24
            'Total_String_Inputs': float(fields[29]) if len(fields) > 29 and fields[29] and fields[29].strip() else 0,  # Seq 29
            'Total_MPPT': float(fields[30]) if len(fields) > 30 and fields[30] and fields[30].strip() else 0,  # Seq 30
            'Night_Consumption_W': float(fields[39]) if len(fields) > 39 and fields[39] and fields[39].strip() else 0,  # Seq 39
        }
        
        return inverter_specs
    except Exception as e:
        st.error(f"Error parsing inverter data: {str(e)}")
        return None

def parse_solar_panel_data(raw_data):
    """Parse solar panel data string and return specifications."""
    try:
        fields = raw_data.split(';')
        
        # First get the basic parameters
        panel_specs = {
            'Manufacturer': str(fields[1]).strip() if len(fields) > 1 else "",  # Seq 1
            'Model': str(fields[2]).strip() if len(fields) > 2 else "",  # Seq 2
            'File_Name': str(fields[3]).strip() if len(fields) > 3 else "",  # Seq 3
            'Data_Source': str(fields[4]).strip() if len(fields) > 4 else "",  # Seq 4
            'Nominal_Power_W': float(fields[7]) if len(fields) > 7 and fields[7] and fields[7].strip() else 0,  # Seq 7
            'Technology': str(fields[11]).strip() if len(fields) > 11 and fields[11] else "",  # Seq 11
            'Cells_in_Series': int(fields[12]) if len(fields) > 12 and fields[12] and fields[12].strip().isdigit() else 0,  # Seq 12
            'Cells_in_Parallel': int(fields[13]) if len(fields) > 13 and fields[13] and fields[13].strip().isdigit() else 0,  # Seq 13
            'Maximum_Voltage_IEC': float(fields[35]) if len(fields) > 35 and fields[35] and fields[35].strip() else 0,  # Seq 35
            'NOCT_C': float(fields[15]) if len(fields) > 15 and fields[15] and fields[15].strip() else 0,  # Seq 15
            'Vmp_V': float(fields[16]) if len(fields) > 16 and fields[16] and fields[16].strip() else 0,  # Seq 16
            'Imp_A': float(fields[17]) if len(fields) > 17 and fields[17] and fields[17].strip() else 0,  # Seq 17
            'Voc_V': float(fields[18]) if len(fields) > 18 and fields[18] and fields[18].strip() else 0,  # Seq 18
            'Isc_A': float(fields[19]) if len(fields) > 19 and fields[19] and fields[19].strip() else 0,  # Seq 19
            'Current_Temp_Coeff': float(fields[20]) if len(fields) > 20 and fields[20] and fields[20].strip() else 0,  # Seq 20
            'Power_Temp_Coeff': float(fields[22]) if len(fields) > 22 and fields[22] and fields[22].strip() else 0,  # Seq 22
            'Module_Length': float(fields[40]) if len(fields) > 40 and fields[40] and fields[40].strip() else 0,  # Seq 40
            'Module_Width': float(fields[41]) if len(fields) > 41 and fields[41] and fields[41].strip() else 0,  # Seq 41
            'Module_Weight': float(fields[43]) if len(fields) > 43 and fields[43] and fields[43].strip() else 0   # Seq 43
        }
        
        # Calculate panel area in square meters
        length_m = panel_specs['Module_Length'] / 1000  # Convert mm to m
        width_m = panel_specs['Module_Width'] / 1000    # Convert mm to m
        panel_specs['Panel_Area_m2'] = round(length_m * width_m, 3)
        
        # Calculate panel efficiency in percentage
        if panel_specs['Panel_Area_m2'] > 0:
            panel_specs['Efficiency_percent'] = round((panel_specs['Nominal_Power_W'] / (panel_specs['Panel_Area_m2'] * 1000)) * 100, 2)
        else:
            panel_specs['Efficiency_percent'] = 0

        return panel_specs
    except Exception as e:
        st.error(f"Error parsing solar panel data: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="PVsyst Component Parser", layout="wide")
    st.title("PVsyst Component Data Parser")
    
    # Create tabs for inverter and panel data
    tab1, tab2 = st.tabs(["Inverter Data", "Solar Panel Data"])
    
    with tab1:
        st.header("Inverter Specifications")
        st.write("Paste inverter data from PVsyst to generate a consolidated Excel file.")
        
        # Initialize session state for inverter inputs
        if 'num_inverters' not in st.session_state:
            st.session_state.num_inverters = 1
        
        # Add inverter button with better visibility
        col1, col2, col3 = st.columns([5, 1, 1])
        with col2:
            if st.button('➕ Add Inverter', key='add_inv', use_container_width=True):
                if st.session_state.num_inverters < 50:  # Increased limit to 50
                    st.session_state.num_inverters += 1
        with col3:
            if st.button('➖ Remove Inverter', key='remove_inv', use_container_width=True):
                if st.session_state.num_inverters > 1:
                    st.session_state.num_inverters -= 1
        
        # Create text input boxes for each inverter
        inverter_data = []
        for i in range(st.session_state.num_inverters):
            with st.container():
                st.subheader(f"Inverter {i + 1}")
                data = st.text_area(
                    "Paste inverter data here",
                    key=f"inverter_{i}",
                    height=100,
                    help="Copy and paste the inverter data string from PVsyst"
                )
                if data:
                    parsed_data = parse_inverter_data(data)
                    if parsed_data:
                        inverter_data.append(parsed_data)
        
        # Generate Excel file for inverters
        if st.button("Generate Inverter Excel File") and inverter_data:
            try:
                df = pd.DataFrame(inverter_data)
                
                # Reorder columns for better readability
                column_order = [
                    'Manufacturer', 'Model', 'File_Name', 'Data_Source',
                    'Nominal_AC_Power_kW', 'Maximum_AC_Power_kW',
                    'Nominal_AC_current_A', 'Maximum_AC_current_A',
                    'Nominal_AC_Voltage_V', 'Phase', 'Frequency_Hz',
                    'Power_threshold_W', 'Nominal_MPP_Voltage_V',
                    'Min_MPP_Voltage_V', 'Max_DC_Voltage_V',
                    'Max_DC_Current_A', 'Total_MPPT',
                    'Total_String_Inputs', 'Night_Consumption_W'
                ]
                
                # Only include columns that exist in the DataFrame
                existing_columns = [col for col in column_order if col in df.columns]
                df = df[existing_columns]
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Inverter Specifications')
                
                output.seek(0)
                st.download_button(
                    label="📥 Download Inverter Excel file",
                    data=output,
                    file_name="consolidated_inverter_specifications.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                st.subheader("Preview of Consolidated Inverter Data")
                st.dataframe(df, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error generating Excel file: {str(e)}")
    
    with tab2:
        st.header("Solar Panel Specifications")
        st.write("Paste solar panel data from PVsyst to generate a consolidated Excel file.")
        
        # Initialize session state for panel inputs
        if 'num_panels' not in st.session_state:
            st.session_state.num_panels = 1
        
        # Add panel button with better visibility
        col1, col2, col3 = st.columns([5, 1, 1])
        with col2:
            if st.button('➕ Add Panel', key='add_panel', use_container_width=True):
                if st.session_state.num_panels < 50:  # Increased limit to 50
                    st.session_state.num_panels += 1
        with col3:
            if st.button('➖ Remove Panel', key='remove_panel', use_container_width=True):
                if st.session_state.num_panels > 1:
                    st.session_state.num_panels -= 1
        
        # Create text input boxes for each panel
        panel_data = []
        for i in range(st.session_state.num_panels):
            with st.container():
                st.subheader(f"Solar Panel {i + 1}")
                data = st.text_area(
                    "Paste solar panel data here",
                    key=f"panel_{i}",
                    height=100,
                    help="Copy and paste the solar panel data string from PVsyst"
                )
                if data:
                    parsed_data = parse_solar_panel_data(data)
                    if parsed_data:
                        panel_data.append(parsed_data)
        
        # Generate Excel file for panels
        if st.button("Generate Panel Excel File") and panel_data:
            try:
                df = pd.DataFrame(panel_data)
                
                # Reorder columns for better readability
                column_order = [
                    'Manufacturer', 'Model', 'File_Name', 'Data_Source',
                    'Nominal_Power_W', 'Technology', 'Cells_in_Series',
                    'Cells_in_Parallel', 'Maximum_Voltage_IEC', 'NOCT_C',
                    'Vmp_V', 'Imp_A', 'Voc_V', 'Isc_A',
                    'Current_Temp_Coeff', 'Power_Temp_Coeff',
                    'Module_Length', 'Module_Width', 'Module_Weight',
                    'Panel_Area_m2', 'Efficiency_percent'
                ]
                
                # Only include columns that exist in the DataFrame
                existing_columns = [col for col in column_order if col in df.columns]
                df = df[existing_columns]
                
                # Format the new columns
                if 'Panel_Area_m2' in df.columns:
                    df['Panel_Area_m2'] = df['Panel_Area_m2'].round(3)
                if 'Efficiency_percent' in df.columns:
                    df['Efficiency_percent'] = df['Efficiency_percent'].round(2)
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Panel Specifications')
                
                output.seek(0)
                st.download_button(
                    label="📥 Download Panel Excel file",
                    data=output,
                    file_name="consolidated_panel_specifications.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                st.subheader("Preview of Consolidated Panel Data")
                st.dataframe(df, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error generating Excel file: {str(e)}")

if __name__ == "__main__":
    main() 
