import json
import os
from datetime import datetime
from typing import List, Optional
import openai
from dotenv import load_dotenv
import os

load_dotenv() 
openai.api_key = os.getenv("OPENAI_API_KEY")
class Destination:
    """Represents a travel destination with all necessary details."""
    
    def __init__(self, city: str, country: str, start_date: str, end_date: str, budget: float, activities: List[str]):
        self.city = city
        self.country = country
        self.start_date = start_date
        self.end_date = end_date
        self.budget = budget
        self.activities = activities
    
    def update_details(self, **kwargs):
        """Update destination details with provided keyword arguments."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __str__(self):
        """Return a formatted string representation of the destination."""
        activities_str = ", ".join(self.activities)
        return f"""
City: {self.city}
Country: {self.country}
Travel Dates: {self.start_date} to {self.end_date}
Budget: ${self.budget:.2f}
Activities: {activities_str}
{'-' * 50}"""
    
    def to_dict(self):
        """Convert destination to dictionary for JSON serialization."""
        return {
            'city': self.city,
            'country': self.country,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'budget': self.budget,
            'activities': self.activities
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create Destination object from dictionary."""
        return cls(
            data['city'],
            data['country'], 
            data['start_date'],
            data['end_date'],
            data['budget'],
            data['activities']
        )


class ItineraryManager:
    """Manages all destination objects and file operations."""
    
    def __init__(self, filename: str = "itinerary.json"):
        self.destinations: List[Destination] = []
        self.filename = filename
        self.load_from_file()
    
    def add_destination(self, destination: Destination):
        """Add a new destination to the itinerary."""
        self.destinations.append(destination)
        print(f"✅ Added {destination.city}, {destination.country} to your itinerary!")
    
    def remove_destination(self, city: str) -> bool:
        """Remove a destination by city name."""
        for i, dest in enumerate(self.destinations):
            if dest.city.lower() == city.lower():
                removed = self.destinations.pop(i)
                print(f"✅ Removed {removed.city}, {removed.country} from your itinerary!")
                return True
        print(f"❌ Destination '{city}' not found!")
        return False
    
    def update_destination(self, city: str) -> bool:
        """Update details of an existing destination."""
        for dest in self.destinations:
            if dest.city.lower() == city.lower():
                print(f"Updating {dest.city}, {dest.country}")
                print("Leave blank to keep current value:")
                
                new_country = input(f"Country ({dest.country}): ").strip()
                if new_country:
                    dest.country = new_country
                
                new_start = input(f"Start Date ({dest.start_date}): ").strip()
                if new_start and self._validate_date(new_start):
                    dest.start_date = new_start
                
                new_end = input(f"End Date ({dest.end_date}): ").strip()
                if new_end and self._validate_date(new_end):
                    dest.end_date = new_end
                
                new_budget = input(f"Budget ({dest.budget}): ").strip()
                if new_budget:
                    try:
                        dest.budget = float(new_budget)
                    except ValueError:
                        print("❌ Invalid budget format!")
                
                new_activities = input(f"Activities (comma-separated): ").strip()
                if new_activities:
                    dest.activities = [act.strip() for act in new_activities.split(',')]
                
                print(f"✅ Updated {dest.city}!")
                return True
        
        print(f"❌ Destination '{city}' not found!")
        return False
    
    def search_destination(self, query: str) -> List[Destination]:
        """Search destinations by city, country, or activities."""
        results = []
        query_lower = query.lower()
        
        for dest in self.destinations:
            if (query_lower in dest.city.lower() or 
                query_lower in dest.country.lower() or
                any(query_lower in activity.lower() for activity in dest.activities)):
                results.append(dest)
        
        return results
    
    def view_all_destinations(self):
        
        if not self.destinations:
            print("📭 No destinations in your itinerary yet!")
            return
        
        print(f"\n🗺️  YOUR TRAVEL ITINERARY ({len(self.destinations)} destinations)")
        print("=" * 60)
        
        for i, dest in enumerate(self.destinations, 1):
            print(f"{i}. {dest}")
    
    def save_to_file(self):
       
        try:
            data = [dest.to_dict() for dest in self.destinations]
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✅ Itinerary saved to {self.filename}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")
    
    def load_from_file(self):
        
        if not os.path.exists(self.filename):
            return
        
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
            
            self.destinations = [Destination.from_dict(item) for item in data]
            print(f"✅ Loaded {len(self.destinations)} destinations from {self.filename}")
        except Exception as e:
            print(f"❌ Error loading file: {e}")
    
    def _validate_date(self, date_str: str) -> bool:
        
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            print("❌ Invalid date format! Use YYYY-MM-DD")
            return False
    
    def sort_by_date(self):
        
        self.destinations.sort(key=lambda x: x.start_date)
        print("✅ Destinations sorted by start date!")
    
    def sort_by_budget(self):
        
        self.destinations.sort(key=lambda x: x.budget)
        print("✅ Destinations sorted by budget!")


class AITravelAssistant:
    """AI-powered travel assistant using OpenAI API."""
    
    def __init__(self, api_key: str = None):
        # Multiple ways to get the API key
        if api_key:
            self.api_key = api_key
        else:
            # Try different environment variable names
            self.api_key = (
                os.getenv("OPENAI_API_KEY") or 
                os.getenv("api_key") or 
                os.getenv("OPENAI_API") or
                os.getenv("OPENAI_KEY")
            )
        
        if not self.api_key:
            print("⚠️  Warning: No OpenAI API key found!")
            print("Set your API key using one of these methods:")
            print("1. Set OPENAI_API_KEY environment variable")
            print("2. Add OPENAI_API_KEY=your_key_here to a .env file")
            print("3. The AI features will be disabled without a valid API key")
            self.client = None
        else:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
                # Test the API key with a simple request
                self._test_api_key()
            except Exception as e:
                print(f"❌ Error initializing OpenAI client: {e}")
                self.client = None
    
    def _test_api_key(self):
        """Test if the API key is valid."""
        try:
            # Make a minimal test request
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print("✅ OpenAI API key validated successfully!")
        except openai.AuthenticationError:
            print("❌ Invalid OpenAI API key! Please check your API key.")
            self.client = None
        except Exception as e:
            print(f"⚠️  Warning: Could not validate API key: {e}")
    
    def is_available(self) -> bool:
        """Check if AI features are available."""
        return self.client is not None
    
    def generate_itinerary(self, destination: Destination) -> str:
        if not self.is_available():
            return self._generate_fallback_itinerary(destination)
        
        try:
            prompt = f"""
Create a detailed daily travel itinerary for {destination.city}, {destination.country}
from {destination.start_date} to {destination.end_date}.
Budget: ${destination.budget} USD.
Preferred Activities: {', '.join(destination.activities)}.

Please provide:
1. Day-by-day schedule
2. Estimated costs for major activities
3. Restaurant recommendations
4. Transportation tips
5. Must-see attractions

Format the response in a clear, organized manner.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful travel planning assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except openai.AuthenticationError:
            return "❌ Authentication failed. Please check your OpenAI API key."
        except openai.RateLimitError:
            return "❌ Rate limit exceeded. Please try again later."
        except Exception as e:
            return f"❌ Error generating itinerary: {e}"
    
    def generate_budget_tips(self, destination: Destination) -> str:
        if not self.is_available():
            return self._generate_fallback_budget_tips(destination)
        
        try:
            prompt = f"""
Provide money-saving tips and budget advice for traveling to {destination.city}, {destination.country}.
Budget: ${destination.budget} USD.
Activities: {', '.join(destination.activities)}.

Include:
1. Budget-friendly accommodation options
2. Cheap local food recommendations
3. Free or low-cost activities
4. Transportation savings
5. General money-saving tips for this destination

Keep it practical and specific to this location.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a budget travel expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except openai.AuthenticationError:
            return "❌ Authentication failed. Please check your OpenAI API key."
        except openai.RateLimitError:
            return "❌ Rate limit exceeded. Please try again later."
        except Exception as e:
            return f"❌ Error generating budget tips: {e}"
    
    def _generate_fallback_itinerary(self, destination: Destination) -> str:
        """Generate a basic itinerary without AI when API is not available."""
        days = (datetime.strptime(destination.end_date, '%Y-%m-%d') - 
                datetime.strptime(destination.start_date, '%Y-%m-%d')).days + 1
        
        itinerary = f"""
🚫 AI Features Unavailable - Basic Itinerary Template

📍 {destination.city}, {destination.country}
📅 {destination.start_date} to {destination.end_date} ({days} days)
💰 Budget: ${destination.budget}
🎯 Activities: {', '.join(destination.activities)}

📋 SUGGESTED DAILY STRUCTURE:
{'='*40}

Day 1: Arrival & City Orientation
- Check into accommodation
- Explore nearby area
- Local restaurant for dinner

Day 2-{days-1}: Main Activities
- Morning: {destination.activities[0] if destination.activities else 'Sightseeing'}
- Afternoon: {destination.activities[1] if len(destination.activities) > 1 else 'Local exploration'}
- Evening: Local cuisine and culture

Day {days}: Departure
- Last-minute shopping/activities
- Check out and travel home

💡 GENERAL TIPS:
- Research local transportation options
- Book accommodations in advance
- Try local street food
- Visit tourist information centers
- Keep emergency contacts handy

⚠️  For detailed, personalized itineraries, please set up your OpenAI API key.
"""
        return itinerary
    
    def _generate_fallback_budget_tips(self, destination: Destination) -> str:
        """Generate basic budget tips without AI."""
        return f"""
🚫 AI Features Unavailable - General Budget Tips

💰 BUDGET TIPS FOR {destination.city.upper()}
{'='*40}

🏠 ACCOMMODATION:
- Consider hostels or budget hotels
- Look for accommodations outside city center
- Book in advance for better rates
- Check for group discounts

🍽️ FOOD & DINING:
- Eat at local markets and street food stalls
- Cook meals if accommodation has kitchen
- Look for lunch specials and happy hours
- Avoid touristy restaurant areas

🚌 TRANSPORTATION:
- Use public transport instead of taxis
- Walk or rent bicycles when possible
- Look for day passes or tourist cards
- Book flights/trains in advance

🎯 ACTIVITIES:
- Look for free walking tours
- Visit free museums on designated days
- Enjoy parks and natural attractions
- Check for student/senior discounts

💡 GENERAL MONEY-SAVING TIPS:
- Set a daily spending limit
- Use budget tracking apps
- Avoid currency exchange at airports
- Negotiate prices at local markets
- Travel during off-peak seasons

⚠️  For location-specific budget advice, please set up your OpenAI API key.
"""


class TravelPlannerApp:
    """Main application class for the travel planner."""
    
    def __init__(self):
        self.manager = ItineraryManager()
        self.ai_assistant = AITravelAssistant()
        
        # Show AI status on startup
        if not self.ai_assistant.is_available():
            print("\n⚠️  AI Features Disabled")
            print("To enable AI features:")
            print("1. Get an API key from https://platform.openai.com/api-keys")
            print("2. Set OPENAI_API_KEY environment variable")
            print("3. Or add OPENAI_API_KEY=your_key to .env file")
    
    def display_menu(self):
        ai_status = "🤖 Available" if self.ai_assistant.is_available() else "🚫 Disabled"
        
        print("\n" + "="*50)
        print("🌍 AI TRAVEL ITINERARY PLANNER")
        print(f"AI Status: {ai_status}")
        print("="*50)
        print("1. Add Destination")
        print("2. Remove Destination") 
        print("3. Update Destination")
        print("4. View All Destinations")
        print("5. Search Destination")
        print("6. AI Travel Assistance")
        print("7. Save Itinerary")
        print("8. Load Itinerary")
        print("9. Sort Destinations")
        print("10. Setup API Key")
        print("11. Exit")
        print("="*50)
    
    def setup_api_key(self):
        """Allow user to set up API key during runtime."""
        print("\n🔑 API KEY SETUP")
        print("-" * 30)
        print("You can get an API key from: https://platform.openai.com/api-keys")
        
        api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
        
        if api_key:
            # Test the new API key
            test_assistant = AITravelAssistant(api_key)
            if test_assistant.is_available():
                self.ai_assistant = test_assistant
                print("✅ API key set successfully! AI features are now available.")
            else:
                print("❌ Invalid API key. Please try again.")
        else:
            print("⏭️  Skipped API key setup.")
    
    def get_destination_input(self) -> Optional[Destination]:
        print("\n📍 ADD NEW DESTINATION")
        print("-" * 30)
        
        city = input("City: ").strip()
        if not city:
            print("❌ City is required!")
            return None
        
        country = input("Country: ").strip()
        if not country:
            print("❌ Country is required!")
            return None
        
        while True:
            start_date = input("Start Date (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
                break
            except ValueError:
                print("❌ Invalid date format! Use YYYY-MM-DD")
        
        while True:
            end_date = input("End Date (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
                if end_date >= start_date:
                    break
                else:
                    print("❌ End date must be after start date!")
            except ValueError:
                print("❌ Invalid date format! Use YYYY-MM-DD")
        
        while True:
            try:
                budget = float(input("Budget (USD): $"))
                if budget > 0:
                    break
                else:
                    print("❌ Budget must be positive!")
            except ValueError:
                print("❌ Invalid budget format!")
        
        activities_input = input("Activities (comma-separated): ").strip()
        if not activities_input:
            print("❌ At least one activity is required!")
            return None
        
        activities = [activity.strip() for activity in activities_input.split(',')]
        
        return Destination(city, country, start_date, end_date, budget, activities)
    
    def ai_assistance_menu(self):
        if not self.manager.destinations:
            print("❌ No destinations available! Add some destinations first.")
            return
        
        if not self.ai_assistant.is_available():
            print("❌ AI features are disabled. Please set up your OpenAI API key first (option 10).")
            return
        
        print("\n🤖 AI TRAVEL ASSISTANCE")
        print("-" * 30)
        print("Available destinations:")
        for i, dest in enumerate(self.manager.destinations, 1):
            print(f"{i}. {dest.city}, {dest.country}")
        
        try:
            choice = int(input("\nSelect destination number: ")) - 1
            if 0 <= choice < len(self.manager.destinations):
                destination = self.manager.destinations[choice]
                
                print("\nAI Assistance Options:")
                print("1. Generate Daily Itinerary")
                print("2. Get Budget Tips")
                
                ai_choice = input("Choose option (1-2): ").strip()
                
                if ai_choice == "1":
                    print(f"\n🗓️ Generating itinerary for {destination.city}...")
                    print("⏳ This may take a moment...")
                    itinerary = self.ai_assistant.generate_itinerary(destination)
                    print(f"\n📋 DAILY ITINERARY FOR {destination.city.upper()}")
                    print("=" * 60)
                    print(itinerary)
                    
                elif ai_choice == "2":
                    print(f"\n💰 Generating budget tips for {destination.city}...")
                    print("⏳ This may take a moment...")
                    tips = self.ai_assistant.generate_budget_tips(destination)
                    print(f"\n💡 BUDGET TIPS FOR {destination.city.upper()}")
                    print("=" * 60)
                    print(tips)
                    
                else:
                    print("❌ Invalid option!")
            else:
                print("❌ Invalid destination number!")
                
        except ValueError:
            print("❌ Invalid input!")
    
    def sort_menu(self):
        if not self.manager.destinations:
            print("❌ No destinations to sort!")
            return
        
        print("\n📊 SORT DESTINATIONS")
        print("-" * 30)
        print("1. Sort by Start Date")
        print("2. Sort by Budget")
        
        choice = input("Choose sorting option (1-2): ").strip()
        
        if choice == "1":
            self.manager.sort_by_date()
        elif choice == "2":
            self.manager.sort_by_budget()
        else:
            print("❌ Invalid option!")
    
    def run(self):
        print("🌍 Welcome to AI Travel Itinerary Planner!")
        
        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-11): ").strip()
            
            if choice == "1":
                destination = self.get_destination_input()
                if destination:
                    self.manager.add_destination(destination)
            
            elif choice == "2":
                city = input("Enter city name to remove: ").strip()
                if city:
                    self.manager.remove_destination(city)
            
            elif choice == "3":
                city = input("Enter city name to update: ").strip()
                if city:
                    self.manager.update_destination(city)
            
            elif choice == "4":
                self.manager.view_all_destinations()
            
            elif choice == "5":
                query = input("Enter search term (city/country/activity): ").strip()
                if query:
                    results = self.manager.search_destination(query)
                    if results:
                        print(f"\n🔍 SEARCH RESULTS ({len(results)} found)")
                        print("=" * 40)
                        for dest in results:
                            print(dest)
                    else:
                        print("❌ No destinations found!")
            
            elif choice == "6":
                self.ai_assistance_menu()
            
            elif choice == "7":
                self.manager.save_to_file()
            
            elif choice == "8":
                self.manager.load_from_file()
            
            elif choice == "9":
                self.sort_menu()
            
            elif choice == "10":
                self.setup_api_key()
            
            elif choice == "11":
                self.manager.save_to_file()
                print("👋 Thank you for using AI Travel Itinerary Planner!")
                print("🌟 Safe travels!")
                break
            
            else:
                print("❌ Invalid choice! Please enter 1-11.")
            
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    app = TravelPlannerApp()
    app.run()