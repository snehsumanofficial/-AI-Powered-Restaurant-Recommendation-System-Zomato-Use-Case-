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
  const [cravings, setCravings] = useState("");
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
    
    // Scale budget input
    let scaledBudget = null;
    if (budget) {
      const val = parseInt(budget);
      if (!isNaN(val)) {
        if (val <= 800) scaledBudget = "low";
        else if (val <= 2000) scaledBudget = "medium";
        else scaledBudget = "high";
      }
    }
    
    try {
      const response = await fetch("http://127.0.0.1:8000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          locality: selectedLocality,
          budget: scaledBudget,
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
    <div>
      {/* Navigation */}
      <nav className={styles.navbar}>
        <div className={styles.logo}>
          <span>zomato</span> AI
        </div>
        <div className={styles.navLinks}>
          <span className={styles.navActive}>Home</span>
          <span>Dining Out</span>
          <span>Delivery</span>
          <span>Profile</span>
        </div>
      </nav>

      {/* Hero Section */}
      <div className={styles.hero}>
        <div className={styles.heroOverlay}></div>
        <div className={styles.modalBox}>
          <h2 className={styles.modalTitle}>Find Your Perfect Meal with Zomato AI</h2>
          
          <div className={styles.searchRow}>
            <input type="text" className={styles.searchInput} placeholder="🎤 Hi! What are you craving today?" value={cravings} onChange={(e) => setCravings(e.target.value)} />
            <button className={styles.sendBtn}>Send</button>
          </div>
          
          <div className={styles.chips}>
            <span className={styles.chip} onClick={() => setCuisine("Italian")}>Italian</span>
            <span className={styles.chip} onClick={() => setCuisine("Spicy")}>Spicy</span>
            <span className={styles.chip} onClick={() => setCuisine("Dessert")}>Dessert</span>
            <span className={styles.chip}>Near Me</span>
          </div>

          <form onSubmit={handleSearch}>
            <div className={styles.formGrid}>
              <div className={styles.inputGroup}>
                <label>LOCALITY</label>
                <select className={styles.inputField} value={selectedLocality} onChange={(e) => setSelectedLocality(e.target.value)} required>
                  <option value="">(e.g. Banashankari)</option>
                  {localities.map(loc => <option key={loc} value={loc}>{loc}</option>)}
                </select>
              </div>
              <div className={styles.inputGroup}>
                <label>CUISINE</label>
                <input type="text" className={styles.inputField} placeholder="(e.g. North Indian)" value={cuisine} onChange={e => setCuisine(e.target.value)} />
              </div>
              <div className={styles.inputGroup}>
                <label>BUDGET (MAX ₹ FOR TWO)</label>
                <input type="text" className={styles.inputField} placeholder="(e.g. 1000)" value={budget} onChange={e => setBudget(e.target.value)} />
              </div>
              <div className={styles.inputGroup}>
                <label>SPECIFIC CRAVINGS</label>
                <input type="text" className={styles.inputField} placeholder="(e.g. Biryani, Butter Chicken)" value={cravings} onChange={e => setCravings(e.target.value)} />
              </div>
            </div>
            
            <div className={styles.moreOptions}>
              ▶ More options
            </div>
            
            <button type="submit" className={styles.submitBtn} disabled={loading}>
              {loading ? "Discovering..." : "Get Recommendations"}
            </button>
          </form>
        </div>
      </div>

      {/* Results Section */}
      {recommendations.length > 0 && (
        <div className={styles.resultsSection}>
          <h2 className={styles.resultsTitle}>Personalized Picks for You</h2>
          <p className={styles.resultsSubtitle}>
            Top recommendations for {cuisine || "any cuisine"} in {selectedLocality || "your area"}, within a budget of {budget || "any"} INR for two and a minimum rating of {minRating}.<br/>
            <small style={{color: '#aaa', marginTop: '5px', display: 'block'}}>Shortlist {recommendations.length} • LLM ranked</small>
          </p>

          <div className={styles.grid}>
            {recommendations.map((rec) => (
              <div key={rec.restaurant_id} className={styles.card}>
                <div className={styles.cardContent}>
                  <div className={styles.cardHeader}>
                    <div className={styles.cardTitle}>{rec.name}</div>
                    <div className={styles.cardRating}>★ {rec.rating || "-"}</div>
                  </div>
                  <div className={styles.cardSub}>
                    {rec.cuisines?.slice(0,3).join(" • ")} • ₹{rec.cost_for_two || "-"} for two
                  </div>
                  <div className={styles.aiReason}>
                    <div className={styles.aiReasonTitle}>AI REASON</div>
                    <div>{rec.explanation}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
