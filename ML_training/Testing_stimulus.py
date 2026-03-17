import numpy as np

def generate_test_prices():
    """Generate two test cases for simulation"""
    
    np.random.seed(42)
    base_price = 50000.0
    
    print("="*70)
    print("Test Stimulus Generator for FPGA Simulation")
    print("="*70)
    
    # ===== TEST 1: LOW VOLATILITY (should trigger LR) =====
    print("\n=== Generating LOW VOLATILITY sample ===")
    
    low_vol_prices = []
    current = base_price
    
    for i in range(60):
        # Very small random walk: ±$2 per step
        change = np.random.randn() * 1.5
        current = current + change
        low_vol_prices.append(current)
    
    spread = max(low_vol_prices) - min(low_vol_prices)
    mean_price = np.mean(low_vol_prices)
    normalized = spread / mean_price
    
    print(f"  Mean price: ${mean_price:.2f}")
    print(f"  Spread: ${spread:.2f}")
    print(f"  Normalized spread: {normalized:.6f}")
    print(f"  Threshold: 0.002000")
    print(f"  Expected: LR (normalized < 0.002)")
    
    # ===== TEST 2: HIGH VOLATILITY (should trigger MLP) =====
    print("\n=== Generating HIGH VOLATILITY sample ===")
    
    high_vol_prices = []
    
    for i in range(60):
        # Large sine wave: ±$400 range
        swing = 350 * np.sin(i / 5.0)
        noise = np.random.randn() * 30
        price = base_price + swing + noise
        high_vol_prices.append(price)
    
    spread = max(high_vol_prices) - min(high_vol_prices)
    mean_price = np.mean(high_vol_prices)
    normalized = spread / mean_price
    
    print(f"  Mean price: ${mean_price:.2f}")
    print(f"  Spread: ${spread:.2f}")
    print(f"  Normalized spread: {normalized:.6f}")
    print(f"  Threshold: 0.002000")
    print(f"  Expected: MLP (normalized > 0.002)")
    
    # ===== Save as HEX files for Verilog =====
    print("\n=== Saving HEX files for Verilog ===")
    
    # Low volatility
    with open('test_prices_low_vol.hex', 'w') as f:
        for price in low_vol_prices:
            # Convert to 32-bit fixed-point (multiply by 256 for 8 fractional bits)
            fixed = int(price * 256) & 0xFFFFFFFF
            f.write(f"{fixed:08X}\n")
    
    print("  ✓ Saved: test_prices_low_vol.hex")
    
    # High volatility
    with open('test_prices_high_vol.hex', 'w') as f:
        for price in high_vol_prices:
            fixed = int(price * 256) & 0xFFFFFFFF
            f.write(f"{fixed:08X}\n")
    
    print("  ✓ Saved: test_prices_high_vol.hex")
    
    # ===== Also save as text for verification =====
    with open('test_prices_readable.txt', 'w') as f:
        f.write("LOW VOLATILITY PRICES:\n")
        for i, p in enumerate(low_vol_prices):
            f.write(f"Price[{i:2d}] = ${p:.2f}\n")
        
        f.write("\n\nHIGH VOLATILITY PRICES:\n")
        for i, p in enumerate(high_vol_prices):
            f.write(f"Price[{i:2d}] = ${p:.2f}\n")
    
    print("  ✓ Saved: test_prices_readable.txt (for reference)")
    
    print("\n" + "="*70)
    print("✓ Test stimulus generation complete!")
    print("="*70)
    print("\nNext step: Add to Vivado simulation")

if __name__ == "__main__":
    generate_test_prices()