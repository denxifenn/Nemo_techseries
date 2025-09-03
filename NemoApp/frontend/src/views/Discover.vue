<script>
export default {
  name: 'Discover',
  data() {
    return {
      componentName: 'Discover'
    }
  }
}
</script>

<template>
  <div>
    <!-- <h1>{{ componentName }}</h1> -->
    <section class="hero">
        <div class="hero-content">
        
        <h1>Explore Events</h1>
            <p>Find and register for the most exciting events happening near you</p>
            
            <div class="search-bar">
                <input type="text" placeholder="Search events...">
                <button>Search</button>
            </div>
        </div>
    </section>
  </div>
</template>

<style>
/* Hero section */
        .hero {
            background: #EC7600;
            padding: 60px 20px;
            text-align: center;
            color: white;
        }
        
        .hero-content {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .hero h1 {
            font-size: 3.2em;
            margin-bottom: 20px;
            font-weight: 700;
        }
        
        .hero p {
            font-size: 1.3em;
            margin-bottom: 40px;
            opacity: 0.95;
        }

        .search-bar {
            background: white;
            padding: 15px 25px;
            border-radius: 50px;
            display: flex;
            max-width: 500px;
            margin: 0 auto 30px;
            box-shadow: 0 4px 15px rgba(255, 255, 255, 0.1);
        }
        
        .search-bar input {
            flex: 1;
            border: none;
            outline: none;
            font-size: 1.1em;
            color: #333; /* dark text for visibility */
            background: transparent; /* removes gray background */
              /* Optionally, add: */
            box-shadow: none;
    }
        
        .search-bar button {
            background: #FFC67B;
            border: none;
            padding: 8px 20px;
            border-radius: 25px;
            color: #ffffff;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        
        .search-bar button:hover {
            background: #FFB85C;
        }
        
        
</style>