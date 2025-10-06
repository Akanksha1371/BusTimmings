import json
from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# --- MOCK BUS SCHEDULE DATA ---
# This data simulates the real bus timings, names, stops, and plate numbers.
# In a real-world application, this would be fetched from a database or an external API.
BUS_SCHEDULES = [
    {
        "bus_name": "Durgamba Motors (AC Sleeper)",
        "plate_number": "KA 19 AC 7701",
        "from_location": "Moodbidri",
        "to_location": "Bengaluru",
        "departure_time": "21:30",
        "reach_time": "06:15",
        "stops": 4,
        "travel_time": "8h 45m"
    },
    {
        "bus_name": "Sugama Tourist (Non-AC Seater)",
        "plate_number": "KA 20 BD 1029",
        "from_location": "Moodbidri",
        "to_location": "Udupi",
        "departure_time": "07:00",
        "reach_time": "08:15",
        "stops": 10,
        "travel_time": "1h 15m"
    },
    {
        "bus_name": "VRL Travels (Multi-Axle Sleeper)",
        "plate_number": "MH 04 AB 9876",
        "from_location": "Moodbidri",
        "to_location": "Mumbai",
        "departure_time": "17:00",
        "reach_time": "10:30 (+1 day)",
        "stops": 12,
        "travel_time": "17h 30m"
    },
    {
        "bus_name": "KSRTC (Rajahamsa Executive)",
        "plate_number": "KA 14 FA 0333",
        "from_location": "Moodbidri",
        "to_location": "Mysuru",
        "departure_time": "15:45",
        "reach_time": "22:50",
        "stops": 7,
        "travel_time": "7h 05m"
    },
    {
        "bus_name": "Anand Travels (AC Seater)",
        "plate_number": "KA 19 EF 2211",
        "from_location": "Moodbidri",
        "to_location": "Hubballi",
        "departure_time": "20:00",
        "reach_time": "04:30",
        "stops": 6,
        "travel_time": "8h 30m"
    },
    {
        "bus_name": "Sugama Tourist (Express)",
        "plate_number": "KA 20 BC 1030",
        "from_location": "Moodbidri",
        "to_location": "Udupi",
        "departure_time": "18:30",
        "reach_time": "19:45",
        "stops": 8,
        "travel_time": "1h 15m"
    },
    {
        "bus_name": "KSRTC (Airavat Club Class)",
        "plate_number": "KA 01 ZZ 0042",
        "from_location": "Moodbidri",
        "to_location": "Bengaluru",
        "departure_time": "22:45",
        "reach_time": "07:30",
        "stops": 3,
        "travel_time": "8h 45m"
    },
]

# Get a list of all unique destination districts for the dropdown
ALL_DISTRICTS = sorted(list(set(bus['to_location'] for bus in BUS_SCHEDULES)))
# Insert a placeholder at the beginning
ALL_DISTRICTS.insert(0, "All Districts")

def generate_bus_card_html(bus):
    """Generates the HTML string for a single bus timing result card."""
    # Use flexbox and responsive design classes for card layout
    return f"""
    <div class="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition duration-300 border-t-4 border-indigo-600 mb-4 w-full">
        <h3 class="text-xl font-bold text-indigo-700 mb-2">{bus['to_location']} Bus</h3>
        
        <!-- Bus Details Section -->
        <div class="grid grid-cols-2 gap-4 text-sm text-gray-700 border-b pb-3 mb-3">
            <p><strong class="text-gray-900">Operator:</strong> {bus['bus_name']}</p>
            <p><strong class="text-gray-900">Plate No.:</strong> {bus['plate_number']}</p>
        </div>

        <!-- Timing and Stops Section -->
        <div class="flex justify-between items-center text-center">
            
            <!-- Departure -->
            <div class="flex-1">
                <p class="text-lg font-extrabold text-green-600">{bus['departure_time']}</p>
                <p class="text-xs text-gray-500">Departure (Moodbidri)</p>
            </div>
            
            <!-- Duration -->
            <div class="flex-1">
                <span class="text-sm font-semibold text-gray-500 block">
                    {bus['travel_time']}
                </span>
                <span class="text-xs text-gray-400">({bus['stops']} Stops)</span>
            </div>

            <!-- Arrival -->
            <div class="flex-1">
                <p class="text-lg font-extrabold text-red-600">{bus['reach_time']}</p>
                <p class="text-xs text-gray-500">Reach Time</p>
            </div>
        </div>
    </div>
    """

def render_results(results, query_district):
    """Renders the list of results into the main container."""
    if not results:
        # Message for no results found
        return f"""
        <div class="text-center py-10">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 19.456l-5.487-5.487a3 3 0 010-4.242L12.456 3.172a3 3 0 014.242 0L20.828 7.586a3 3 0 010 4.242l-5.487 5.487M9.172 19.456l-5.487-5.487M9.172 19.456l3.37-3.37m-5.656 1.414l-1.414 1.414" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">No Buses Found</h3>
            <p class="mt-1 text-sm text-gray-500">
              There are no direct bus schedules available from Moodbidri to {query_district}.
            </p>
            <div class="mt-6">
                <a href="/" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                    Show All Timings
                </a>
            </div>
        </div>
        """
    
    # Generate HTML cards for each bus
    cards = "".join(generate_bus_card_html(bus) for bus in results)
    
    # Determine the heading based on the search query
    heading_text = f"Timings to {query_district}" if query_district != "All Districts" else "All Available Bus Timings from Moodbidri"

    return f"""
        <h2 class="text-2xl font-semibold text-gray-800 mb-6 border-b pb-2">{heading_text}</h2>
        <div class="max-w-xl mx-auto md:max-w-3xl">
            {cards}
        </div>
    """

# --- FLASK ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def index():
    # Default behavior is to show all schedules
    results = BUS_SCHEDULES
    query_district = "All Districts"
    
    # Check if a form submission from the search route redirected here (POST handling is simplified below)
    if request.method == 'POST':
        # This branch shouldn't typically be hit if we use the /search route, 
        # but serves as a fallback or for initial display logic.
        pass

    # Render the page with all results initially
    content_html = render_results(results, query_district)
    return render_template_string(HTML_TEMPLATE, 
                                  districts=ALL_DISTRICTS, 
                                  content_html=content_html,
                                  current_district=query_district)

@app.route('/search', methods=['POST'])
def search_timings():
    # Extract the 'to' address from the form submission
    to_district = request.form.get('to_address', 'All Districts')
    
    if to_district == "All Districts":
        # If "All Districts" is selected, show everything
        filtered_results = BUS_SCHEDULES
    else:
        # Filter the schedules based on the selected district
        filtered_results = [
            bus for bus in BUS_SCHEDULES 
            if bus['to_location'].lower() == to_district.lower()
        ]

    # Generate the resulting HTML to display
    content_html = render_results(filtered_results, to_district)

    # Render the main template with the search results
    return render_template_string(HTML_TEMPLATE, 
                                  districts=ALL_DISTRICTS, 
                                  content_html=content_html,
                                  current_district=to_district)

# --- HTML TEMPLATE (Single File Mandate) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Moodbidri Bus Timings</title>
    <!-- Load Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Custom font for a clean, modern look */
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f4f7f9;
        }
        /* Style for the select dropdown to ensure readability and aesthetic */
        .select-custom {
            -webkit-appearance: none;
            -moz-appearance: none;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'%3E%3Cpath d='M9.293 12.95l.707.707L15 9.293V2H5v7.293l5.586 5.586z' fill='%236B7280'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 0.75rem center;
            background-size: 0.8rem 0.8rem;
        }
    </style>
</head>
<body>
    <div class="min-h-screen p-4 sm:p-8">
        <div class="max-w-4xl mx-auto">
            
            <!-- Header -->
            <header class="text-center mb-10 p-6 bg-white rounded-xl shadow-md">
                <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">Moodbidri Bus Timings Explorer</h1>
                <p class="mt-2 text-lg text-gray-500">Search for routes from Moodbidri to major districts.</p>
            </header>

            <!-- Search Form -->
            <div class="bg-white p-6 rounded-xl shadow-lg mb-8">
                <form action="{{ url_for('search_timings') }}" method="POST" class="grid grid-cols-1 md:grid-cols-5 gap-4 items-end">
                    
                    <!-- From Location (Fixed) -->
                    <div class="col-span-2">
                        <label for="from_address" class="block text-sm font-medium text-gray-700 mb-1">From Address</label>
                        <input type="text" id="from_address" name="from_address" value="Moodbidri" readonly class="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-100 cursor-not-allowed focus:outline-none">
                    </div>

                    <!-- To Location (Dropdown) -->
                    <div class="col-span-2">
                        <label for="to_address" class="block text-sm font-medium text-gray-700 mb-1">To District / Location</label>
                        <select id="to_address" name="to_address" class="select-custom w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 shadow-sm transition duration-150 ease-in-out">
                            {% for district in districts %}
                                <option value="{{ district }}" {% if district == current_district %}selected{% endif %}>{{ district }}</option>
                            {% endfor %}
                        </select>
                    </div>

                    <!-- Search Button -->
                    <div class="col-span-1">
                        <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg shadow-md transition duration-200 ease-in-out transform hover:scale-105">
                            Search
                        </button>
                    </div>
                </form>
            </div>

            <!-- Results Section -->
            <main id="results-container" class="mt-8">
                {{ content_html | safe }}
            </main>

        </div>
    </div>
</body>
</html>
"""

# This block ensures the application runs when the file is executed directly
if __name__ == '__main__':
    # Flask uses '0.0.0.0' and port 8080 or similar in deployment environments
    # For local running, we use the default host and port for development
    app.run(debug=True)
