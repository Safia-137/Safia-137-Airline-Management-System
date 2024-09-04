from flask import Flask, request, render_template, redirect, flash
import mysql.connector
from datetime import datetime, timedelta, date


app = Flask(__name__)
app.secret_key = 'root'  # Necessary for flashing messages

# Function to get the database connection
def get_db_connection():
    try:
        con = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='project'
        )
        return con
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
@app.route('/')
def index():
    return render_template('index.html')

# Staff management routes

@app.route('/add_staff', methods=['GET', 'POST'])
def add_staff():
    con = get_db_connection()
    if not con:
        flash('Database connection error.')
        return render_template('add_staff.html')
    
    cursor = con.cursor(dictionary=True)
    
    if request.method == 'POST':
        if 'add_staff' in request.form:
            try:
                # Establish cursor connection
                cursor = con.cursor()
                
                # Get the next Staff_Id
                cursor.execute("SELECT MAX(Staff_Id) FROM Staff_Details")
                resultset = cursor.fetchone()
                Staff_Id = 1 if resultset[0] is None else resultset[0] + 1

                # Collect input from form
                Staff_Name = request.form['name']
                Staff_Nationality = request.form['nationality']
                Staff_Email_Id = request.form['email']
                Hire_Date = datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date()
                Date_Today = datetime.today().date()
                Employment_Duration = (Date_Today - Hire_Date).days
                No_Annual_Leaves = int(request.form['annual_leaves'])

                # Fetch designation choice from the dropdown
                choice = request.form['designation']  # This will be '1', '2', '3', or '4'

                # Determine Designation and Salary
                if choice == "1":
                    Designation = "Pilot"
                    Starting_monthly_salary = 70000
                elif choice == "2":
                    Designation = "Co-Pilot"
                    Starting_monthly_salary = 60000
                elif choice == "3":
                    Designation = "Stewardess/Steward"
                    Starting_monthly_salary = 45000
                elif choice == "4":
                    Designation = "Ground Staff"
                    Starting_monthly_salary = 30000
                else:
                    flash("Invalid Designation")
                    return render_template('staff.html')

                # Calculate Seniority Level and Monthly Salary
                Num_of_years = Date_Today.year - Hire_Date.year
                if Num_of_years == 0:
                    Seniority_Level = "Entry Level"
                    Monthly_Salary = Starting_monthly_salary
                elif 1 <= Num_of_years <= 5:
                    Seniority_Level = "Intermediate"
                    Monthly_Salary = int(Starting_monthly_salary * 1.1)
                elif 6 <= Num_of_years <= 10:
                    Seniority_Level = "Mid-Senior"
                    Monthly_Salary = int(Starting_monthly_salary * 1.15)
                elif Num_of_years > 10:
                    Seniority_Level = "Senior"
                    Monthly_Salary = int(Starting_monthly_salary * 1.2)
                else:
                    flash("Invalid Experience")
                    return render_template('add_staff.html')

                # Insert into Staff_Details table
                sql = """
                    INSERT INTO Staff_Details (Staff_Id, Staff_Name, Staff_Nationality, Staff_Email_Id, Designation, Hire_Date, Employment_Duration, Seniority_Level, Monthly_Salary, No_Annual_Leaves)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (Staff_Id, Staff_Name, Staff_Nationality, Staff_Email_Id, Designation, Hire_Date, Employment_Duration, Seniority_Level, Monthly_Salary, No_Annual_Leaves))
                con.commit()

                flash('Staff member added successfully!')
                return redirect('/add_staff')
            except Exception as e:
                flash(f"An error occurred: {str(e)}")
            finally:
                cursor.close()
                con.close()
        return redirect('/add_staff')

    return render_template('add_staff.html')

@app.route('/search_staff', methods=['GET', 'POST'])
def search_staff():
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    if request.method == 'POST':
        staff_id = request.form['staff_id']
        
        cursor.execute("SELECT * FROM Staff_Details WHERE Staff_Id = %s", (staff_id,))
        staff_details = cursor.fetchone()  # Fetch only one record based on the Staff_Id
        
        if staff_details:
            # Render the template with staff details
            return render_template('search_staff.html', staff_details=staff_details)
        else:
            # Flash a message if no staff found
            flash(f'No staff found with ID {staff_id}', 'info')
            return render_template('search_staff.html', staff_details=None)
    
    # Render the search page without staff details by default
    return render_template('search_staff.html', staff_details=None)

@app.route('/delete_staff', methods=['GET', 'POST'])
def delete_staff():
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    if request.method == 'POST':
        staff_id = request.form['staff_id']

        # Check if the staff ID exists
        cursor.execute("SELECT Staff_Id FROM Staff_Details WHERE Staff_Id = %s", (staff_id,))
        staff_exists = cursor.fetchone()

        if staff_exists:
            # Perform deletion
            cursor.execute("DELETE FROM Staff_Details WHERE Staff_Id = %s", (staff_id,))
            con.commit()
            flash('Staff record deleted successfully!', 'success')
        else:
            flash(f'No staff found with ID {staff_id}', 'info')

        return redirect('/delete_staff')

    return render_template('delete_staff.html')

@app.route('/edit_staff', methods=['GET', 'POST'])
def edit_staff():
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    if request.method == 'POST':
        staff_id = request.form['staff_id']
        staff_name = request.form['name']
        staff_nationality = request.form['nationality']
        staff_email = request.form['email']
        hire_date = request.form['hire_date']
        annual_leaves = request.form['annual_leaves']
        designation = request.form['designation']
        if designation == "1":
            designation = "Pilot"
            starting_monthly_salary = 70000
        elif designation == "2":
            designation = "Co-Pilot"
            starting_monthly_salary = 60000
        elif designation == "3":
            designation = "Stewardess/Steward"
            starting_monthly_salary = 45000
        elif designation == "4":
            designation = "Ground Staff"
            starting_monthly_salary = 30000

        # Calculate Seniority Level and Monthly Salary
        hire_date_obj = datetime.strptime(hire_date, '%Y-%m-%d').date()
        current_year = datetime.today().year
        hire_year = hire_date_obj.year
        years_of_experience = current_year - hire_year

        if years_of_experience == 0:
            seniority_level = "Entry Level"
            monthly_salary = starting_monthly_salary
        elif 1 <= years_of_experience <= 5:
            seniority_level = "Intermediate"
            monthly_salary = starting_monthly_salary * 1.10
        elif 6 <= years_of_experience <= 10:
            seniority_level = "Mid-Senior"
            monthly_salary = starting_monthly_salary * 1.15
        else:
            seniority_level = "Senior"
            monthly_salary = starting_monthly_salary * 1.20
        cursor.execute("SELECT * FROM Staff_Details WHERE Staff_Id = %s", (staff_id,))
        staff = cursor.fetchone()
        if staff:
            cursor.execute("""
                UPDATE Staff_Details
                SET Staff_Name = %s, Staff_Nationality = %s, Staff_Email_Id = %s, Hire_Date = %s, No_Annual_Leaves = %s, Designation = %s, Seniority_Level = %s, Monthly_Salary = %s
                WHERE Staff_Id = %s
            """, (staff_name, staff_nationality, staff_email, hire_date, annual_leaves, designation, seniority_level, monthly_salary, staff_id))
            con.commit()

            flash('Staff record updated successfully!', 'success')
            return redirect('/edit_staff')
        else:
            flash('No staff found with that ID', 'info')
            return redirect('/edit_staff')
        # Update staff record
        

    return render_template('edit_staff.html')

@app.route('/add_aircraft', methods=['GET', 'POST'])
def add_aircraft():
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    if request.method == 'POST':
        cursor = con.cursor()
        
        # Fetch the next Aircraft_Id
        cursor.execute("SELECT MAX(Aircraft_Id) FROM Aircraft_Details")
        resultset = cursor.fetchone()
        Aircraft_Id = 1 if resultset[0] is None else resultset[0] + 1
        
        # Retrieve form data
        Aircraft_Type = request.form['aircraft_type']
        Manufacturing_Company = request.form['manufacturing_company']
        Seating_Capacity = int(request.form['seating_capacity'])
        Hours_Flown = float(request.form['hours_flown'])
        Last_Service_Date_str = request.form['last_service_date']
        Last_Service_Date = datetime.strptime(Last_Service_Date_str, '%Y-%m-%d').date()
        Next_Service_Date = Last_Service_Date + timedelta(days=365)
        
        # Insert data into database
        sql = """
        INSERT INTO Aircraft_Details 
        (Aircraft_Id, Aircraft_Type, Manufacturing_Company, Seating_Capacity, Hours_Flown, Last_Service_Date, Next_Service_Date) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (Aircraft_Id, Aircraft_Type, Manufacturing_Company, Seating_Capacity, Hours_Flown, Last_Service_Date, Next_Service_Date)
        cursor.execute(sql, values)
        con.commit()
        cursor.close()
        
        flash('Aircraft details added successfully!', 'success')
        return redirect('/add_aircraft')
    
    return render_template('add_aircraft.html')

@app.route('/search_aircraft', methods=['GET', 'POST'])
def search_aircraft():
    if request.method == 'POST':
        aircraft_id = request.form['aircraft_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        # Correcting the SQL placeholder from ? to %s
        sql = "SELECT * FROM Aircraft_Details WHERE Aircraft_Id = %s"
        cursor.execute(sql, (aircraft_id,))
        resultset = cursor.fetchall()
        conn.close()

        if resultset:
            return render_template('search_aircraft.html', aircraft_details=resultset[0])
        else:
            flash('No records found for Aircraft ID: {}'.format(aircraft_id), 'info')
            return redirect('/search_aircraft')

    return render_template('search_aircraft.html')


@app.route('/delete_aircraft', methods=['GET', 'POST'])
def delete_aircraft():
    if request.method == 'POST':
        con = get_db_connection()
        cursor = con.cursor()
        aircraft_id = request.form.get('aircraft_id')
        cursor = con.cursor()

        # Check if the aircraft ID exists
        check_sql = 'SELECT Aircraft_Id FROM Aircraft_Details WHERE Aircraft_Id = %s'
        cursor.execute(check_sql, (aircraft_id,))
        result = cursor.fetchone()

        if not result:
            flash('Aircraft does not exist.', 'danger')
        else:
            # Delete the record
            delete_sql = 'DELETE FROM Aircraft_Details WHERE Aircraft_Id = %s'
            cursor.execute(delete_sql, (aircraft_id,))
            con.commit()
            flash('Deleted Successfully.', 'success')

    return render_template('delete_aircraft.html')

@app.route('/edit_aircraft', methods=['GET', 'POST'])
def edit_aircraft():
    aircraft_details = None

    if request.method == 'POST':
        con = get_db_connection()
        cursor = con.cursor(dictionary=True)
        
        # Get the aircraft_id from the form
        aircraft_id = request.form.get('aircraft_id')

        if aircraft_id:
            # Check if aircraft exists in the database
            cursor.execute("SELECT * FROM Aircraft_Details WHERE Aircraft_Id = %s", (aircraft_id,))
            aircraft_details = cursor.fetchone()
            
            if not aircraft_details:
                # Aircraft does not exist
                flash("Aircraft with ID {} does not exist.".format(aircraft_id), "danger")
            else:
                # Only proceed if the aircraft exists
                # Get other details from the form
                aircraft_type = request.form.get('aircraft_type')
                manufacturing_company = request.form.get('manufacturing_company')
                seating_capacity = request.form.get('seating_capacity')
                hours_flown = request.form.get('hours_flown')
                last_service_date = request.form.get('last_service_date')

                # Ensure all fields are provided
                if aircraft_type and manufacturing_company and seating_capacity and hours_flown and last_service_date:
                    # Calculate the next service date based on the last service date
                    last_service_date_obj = datetime.strptime(last_service_date, '%Y-%m-%d')
                    next_service_date_obj = last_service_date_obj + timedelta(days=365)
                    next_service_date = next_service_date_obj.strftime('%Y-%m-%d')
                    
                    # Update the aircraft details in the database
                    cursor.execute("""
                        UPDATE Aircraft_Details
                        SET Aircraft_Type = %s, Manufacturing_Company = %s, Seating_Capacity = %s,
                            Hours_Flown = %s, Last_Service_Date = %s, Next_Service_Date = %s
                        WHERE Aircraft_Id = %s
                    """, (aircraft_type, manufacturing_company, seating_capacity, hours_flown, last_service_date, next_service_date, aircraft_id))
                    
                    con.commit()
                    flash("Aircraft details updated successfully!", "success")
                else:
                    flash("All fields must be filled out to update the aircraft details.", "warning")
        else:
            flash("Aircraft ID is required.", "warning")

    # Render the edit page with current aircraft data if found
    return render_template('edit_aircraft.html', aircraft_details=aircraft_details)

@app.route('/add_journey_log', methods=['GET', 'POST'])
def add_journey_log():
    if request.method == 'POST':
        con = get_db_connection()
        aircraft_id = request.form.get('aircraft_id')
        flight_date = request.form.get('flight_date')
        departure_airport = request.form.get('departure_airport')
        arrival_airport = request.form.get('arrival_airport')
        flight_duration = request.form.get('flight_duration')
        pilot_name = request.form.get('pilot_name')

        cursor = con.cursor()
        # Check if Aircraft_Id exists
        cursor.execute("SELECT 1 FROM Aircraft_Details WHERE Aircraft_Id = %s", (aircraft_id,))
        if cursor.fetchone() is None:
            flash('The Aircraft ID does not exist. Please enter a valid Aircraft ID.', 'danger')
            return render_template('add_journey_log.html')

        # Insert the journey log
        try:
            cursor.execute(
                """INSERT INTO Journey_Log (Aircraft_Id, Flight_Date, Departure_Airport, Arrival_Airport, Flight_Duration, Pilot_Name)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (aircraft_id, flight_date, departure_airport, arrival_airport, flight_duration, pilot_name)
            )
            con.commit()
            flash('Journey log added successfully!', 'success')
            return redirect('/add_journey_log')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('add_journey_log.html')

@app.route('/view_journey_log', methods=['GET', 'POST'])
def view_journey_log():
    if request.method == 'POST':
        aircraft_id = request.form['aircraft_id']
        con = get_db_connection()
        cursor = con.cursor(dictionary=True)
        try:
            # Check if the aircraft ID exists in the Aircraft_Details table
            cursor.execute("SELECT * FROM Aircraft_Details WHERE Aircraft_Id = %s", (aircraft_id,))
            if not cursor.fetchone():
                flash("Aircraft ID does not exist.", "danger")
                return render_template('view_journey_log.html')

            # Query to get journey logs for the specified aircraft ID
            cursor.execute("SELECT * FROM Journey_Log WHERE Aircraft_Id = %s", (aircraft_id,))
            journey_logs = cursor.fetchall()

            return render_template('view_journey_log.html', journey_logs=journey_logs, aircraft_id=aircraft_id)

        except mysql.connector.Error as err:
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()

    return render_template('view_journey_log.html')

if __name__ == '__main__':
    app.run(debug=True)
