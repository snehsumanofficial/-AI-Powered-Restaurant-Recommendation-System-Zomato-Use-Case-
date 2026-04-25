"use client";

import { useEffect, useState } from 'react';
import styles from './page.module.css';

interface RestaurantInfo {
  restaurant_id: string;
  rank: number;
  name: string;
  locality: string;
  cuisines: string[];
  rating: number | null;
  cost_for_two: number | null;
  cost_tier: string | null;
  explanation: string;
}

export default function Home() {
  const [localities, setLocalities] = useState<string[]>([]);
  const [recommendations, setRecommendations] = useState<RestaurantInfo[]>([]);
  const [loading, setLoading] = useState(false);
  
  const [selectedLocality, setSelectedLocality] = useState("");
  const [budget, setBudget] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [minRating, setMinRating] = useState("3.5");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/localities")
      .then(res => res.json())
      .then(data => {
        if (data.localities) {
          setLocalities(data.localities);
          if (data.localities.length > 0) setSelectedLocality(data.localities[0]);
        }
      })
      .catch(console.error);
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setRecommendations([]);
    
    try {
      const response = await fetch("http://127.0.0.1:8000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          locality: selectedLocality,
          budget: budget || null,
          cuisine: cuisine || null,
          min_rating: parseFloat(minRating) || 0
        })
      });
      const data = await response.json();
      if (data.recommendations) {
        setRecommendations(data.recommendations);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      
      {/* Tabs */}
      <div className={styles.tabs}>
        <div className={`${styles.tab} ${styles.tabActive}`}>
          <span style={{fontSize: '1.5rem'}}>🍽️</span> Dining Out
        </div>
        <div className={styles.tab}>
          <span style={{fontSize: '1.5rem'}}>🛵</span> Delivery
        </div>
        <div className={styles.tab}>
          <span style={{fontSize: '1.5rem'}}>🍹</span> Nightlife
        </div>
      </div>

      {/* Hero Banner */}
      <div className={styles.banner}>
        <div className={styles.bannerContent}>
          <h2>Get up to</h2>
          <h1>50% <span style={{fontSize:'2rem'}}>OFF</span></h1>
          <p>on your dining bills with Zomato AI</p>
          <button className={styles.bannerBtn}>Check out all the restaurants</button>
        </div>
      </div>

      <h2>Restaurants in {selectedLocality || "your area"}</h2>
      <br/>

      {/* Filters Form */}
      <form onSubmit={handleSearch} className={styles.searchBox}>
        <div className={styles.formGrid}>
          <div className={styles.inputGroup}>
            <label>Locality</label>
            <select 
              className={styles.inputField}
              value={selectedLocality}
              onChange={(e) => setSelectedLocality(e.target.value)}
              required
            >
              <option value="">Select a locality</option>
              {localities.map(loc => <option key={loc} value={loc}>{loc}</option>)}
            </select>
          </div>
          
          <div className={styles.inputGroup}>
            <label>Budget Level</label>
            <select 
              className={styles.inputField}
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
            >
              <option value="">Any</option>
              <option value="low">Low Budget (≤ ₹800)</option>
              <option value="medium">Medium Budget (≤ ₹2000)</option>
              <option value="high">Premium</option>
            </select>
          </div>

          <div className={styles.inputGroup}>
            <label>Cuisine</label>
            <input 
              type="text" 
              className={styles.inputField} 
              placeholder="e.g. North Indian" 
              value={cuisine}
              onChange={(e) => setCuisine(e.target.value)}
            />
          </div>

          <div className={styles.inputGroup}>
            <label>Minimum Rating</label>
            <input 
              type="number" 
              step="0.1" 
              min="0" 
              max="5" 
              className={styles.inputField} 
              value={minRating}
              onChange={(e) => setMinRating(e.target.value)}
            />
          </div>
        </div>
        <button type="submit" className={styles.submitBtn} disabled={loading}>
          {loading ? "Discovering..." : "Get AI Recommendations"}
        </button>
      </form>

      {/* Results */}
      <div className={styles.grid}>
        {recommendations.map((rec) => (
          <div key={rec.restaurant_id} className={styles.card}>
            <div 
              className={styles.cardImage} 
              style={{backgroundImage: `url('https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80')`, backgroundSize: 'cover', backgroundPosition: 'center'}}
            />
            <div className={styles.cardContent}>
              <div className={styles.cardHeader}>
                <div className={styles.cardTitle}>{rec.name}</div>
                <div className={styles.cardRating}>{rec.rating || "-"} ★</div>
              </div>
              <div className={styles.cardSub}>
                <span>{rec.cuisines?.slice(0,2).join(", ")}</span>
                <span>₹{rec.cost_for_two || "-"} for two</span>
              </div>
              <div className={styles.cardSub} style={{fontSize: '0.8rem'}}>
                <span>{rec.locality}</span>
              </div>
              {rec.explanation && (
                <div className={styles.cardExplanation}>
                  ✨ {rec.explanation}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      
    </div>
  );
}
