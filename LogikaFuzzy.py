import streamlit as st


# ====== Fuzzifikasi per variabel ======
#AGE
def age_young(a):
    if a <= 25:
        return 1
    elif 25 < a < 45:
        return (45 - a) / (45 - 25)
    else:
        return 0

def age_adult(a):
    if 35 <= a < 45:
        return (a - 35) / (45 - 35)
    elif 45 <= a <= 55:
        return (55 - a) / (55 - 45)
    else:
        return 0

def age_old(a):
    if a <= 45:
        return 0
    elif 45 < a < 65:
        return (a - 45) / (65 - 45)
    else:
        return 1


#GLUCOSE
def glucose_low(g):
    if g <= 50:
        return 1
    elif g <= 90:
        return (90 - g) / (90 - 50)
    else:
        return 0

def glucose_high(g):
    if g <= 60:
        return 0
    elif g <= 100:
        return (g - 60) / (100 - 60)
    else:
        return 1

#BMI
def bmi_low(b):
    if b <= 10:
        return 1
    elif b <= 30:
        return (30 - b) / (30 - 10)
    else:
        return 0

def bmi_mid(b):
    if 20 <= b < 30:
        return (b - 20) / (30 - 20)
    elif 30 < b <= 40:
        return (40 - b) / (40 - 30)
    else:
        return 0

def bmi_high(b):
    if b <= 30:
        return 0
    elif 40 < b < 50:
        return (b - 40) / (50 - 40)
    else:
        return 1

#CIGARETTE
def cigarette_low(c):
    if c <= 5:
        return 1
    elif c <= 30:
        return (30 - c) / (30 - 5)
    else:
        return 0

def cigarette_high(c):
    if c <= 15:
        return 0
    elif c <= 45:
        return (c - 15) / (45 - 15)
    else:
        return 1

def fuzzify_age(age):
    return {
        "Young": age_young(age),
        "Adult": age_adult(age),
        "Old": age_old(age)
    }

def fuzzify_glucose(glu):
    return {
        "Low": glucose_low(glu),
        "High": glucose_high(glu)
    }

def fuzzify_bmi(bmi):
    return {
        "Low": bmi_low(bmi),
        "Mid": bmi_mid(bmi),
        "High": bmi_high(bmi)
    }

def fuzzify_cigarette(cigarette):
    return {
        "Low": cigarette_low(cigarette),
        "High": cigarette_high(cigarette)
    }



# ====== Semua aturan (36 rules) ======
def build_rules():
    rules = []
    ages = ["Young", "Adult", "Old"]
    gls = ["Low", "High"]
    bmis = ["Low", "Mid", "High"]
    cigs = ["Low", "High"]
    for a in ages:
        for g in gls:
            for b in bmis:
                for c in cigs:
                    if a == "Young":
                        if g == "Low" and b == "High" and c == "High":
                            out = 1
                        elif g == "High" and (
                            (b == "High") or (b == "Mid" and c == "High") or (b == "Low" and c == "High")
                        ):
                            out = 1
                        else:
                            out = 0
                    elif a == "Adult":
                        if g == "Low" and b == "Mid" and c == "High":
                            out = 1
                        elif g == "Low" and b == "High" and c == "High":
                            out = 1
                        elif g == "High" and ((b == "Low" and c == "High") or b in ["Mid", "High"]):
                            out = 1
                        else:
                            out = 0
                    else:
                        if g == "Low" and b == "Low" and c == "Low":
                            out = 0
                        elif g == "Low" and b == "Mid" and c == "Low":
                            out = 0
                        else:
                            out = 1
                    rules.append({"Age": a, "Glucose": g, "BMI": b, "Cigarette": c, "Output": out})
    return rules


# ====== Defuzzifikasi Tsukamoto ======
def defuzzify(inferences):
    if not inferences:
        return 0
    total_alpha = sum([inf["alpha"] for inf in inferences])
    total_az = sum([inf["alpha"] * inf["z"] for inf in inferences])
    return total_az / total_alpha if total_alpha != 0 else 0

# ====== STREAMLIT APP ======
st.set_page_config(page_title="Fuzzy Tsukamoto - Stroke Predictor", layout="wide")
st.title("\U0001F9E0 Prediksi Stroke dengan Logika Fuzzy Tsukamoto")

# === 1. Input ===
st.header("1\u20e3 Input Data")
col1, col2 = st.columns(2)
with col1:
    age = st.slider("Age", 0.0, 100.0, 35.0, step=0.1)
    bmi = st.slider("BMI", 0.0, 50.0, 25.0, step=0.1)
with col2:
    glucose = st.slider("Glucose", 0.0, 100.0, 75.0, step=0.1)
    cigarette = st.slider("Cigarette", 0.0, 100.0, 15.0, step=0.1)

# === 2. Fuzzyfikasi ===
st.header("2\u20e3 Fuzzyfikasi (Tingkat Keanggotaan)")

age_fz = fuzzify_age(age)
glucose_fz = fuzzify_glucose(glucose)
bmi_fz = fuzzify_bmi(bmi)
cig_fz = fuzzify_cigarette(cigarette)

fz_data = {
    "Age": age_fz,
    "Glucose": glucose_fz,
    "BMI": bmi_fz,
    "Cigarette": cig_fz
}
for var, fz in fz_data.items():
    if var is not None and str(var).strip() != "":
        try:
            st.subheader(f"🔹 {str(var)}")
        except Exception as e:
            st.warning(f"Gagal menampilkan subheader untuk: {var}. Error: {e}")

    st.json({k: round(v, 4) for k, v in fz.items()})

# === 3. Rule Evaluation ===
st.header("3\u20e3 Inferensi (Evaluasi Aturan Fuzzy)")

rules = build_rules()
inferences = []

for i, rule in enumerate(rules):
    α = min(
        age_fz.get(rule["Age"], 0),
        glucose_fz.get(rule["Glucose"], 0),
        bmi_fz.get(rule["BMI"], 0),
        cig_fz.get(rule["Cigarette"], 0)
    )
    if α > 0:
        z = α if rule["Output"] == 1 else 1 - α

        inferences.append({
            "Rule": f"R{i+1}",
            "Age": rule["Age"],
            "Glucose": rule["Glucose"],
            "BMI": rule["BMI"],
            "Cigarette": rule["Cigarette"],
            "Output": "Stroke" if rule["Output"] == 1 else "Not Stroke",
            "alpha": round(α, 4),
            "z": round(z, 4),
            "α*z": round(α * z, 4)
        })

if inferences:
    st.dataframe(inferences, use_container_width=True)
else:
    st.warning("Tidak ada aturan yang aktif (α > 0)")

# === 4. Defuzzifikasi ===
st.header("4\u20e3 Defuzzifikasi")
z_final = defuzzify(inferences)

if inferences:
    total_alpha = sum([row["alpha"] for row in inferences])
    total_az = sum([row["alpha"] * row["z"] for row in inferences])
    st.latex(r"z = \frac{\sum (\alpha \cdot z)}{\sum \alpha} = " +
             f"{total_az:.4f} / {total_alpha:.4f} = {z_final:.4f}")
else:
    st.info("Tidak dapat menghitung defuzzifikasi karena tidak ada aturan aktif.")

# === 5. Hasil Akhir ===
st.header("5\u20e3 Hasil Prediksi")
if z_final >= 0.5:
    st.error(f"\u26a0\ufe0f STROKE ({z_final:.4f})")
else:
    st.success(f"\u2705 Tidak stroke ({z_final:.4f})")
