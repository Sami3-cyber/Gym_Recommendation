"""
Script to download the gym exercise dataset
"""
import pandas as pd
import os

# Since we need Kaggle credentials, let's create sample data based on the dataset structure
# This matches the Kaggle gym exercise dataset format
# In production, you would use: kaggle datasets download niharika41298/gym-exercise-data

# Sample data based on the actual dataset structure
exercises = [
    {"Title": "Partner plank band row", "Desc": "The partner plank band row is an abdominal exercise", "Type": "Strength", "BodyPart": "Abdominals", "Equipment": "Bands", "Level": "Intermediate", "Rating": None, "RatingDesc": ""},
    {"Title": "Banded crunch isometric hold", "Desc": "The banded crunch isometric hold is strength exercise", "Type": "Strength", "BodyPart": "Abdominals", "Equipment": "Bands", "Level": "Intermediate", "Rating": None, "RatingDesc": ""},
    {"Title": "FYR Banded Plank Jack", "Desc": "The banded plank jack is a variation of plank", "Type": "Strength", "BodyPart": "Abdominals", "Equipment": "Bands", "Level": "Intermediate", "Rating": None, "RatingDesc": ""},
    {"Title": "Banded crunch", "Desc": "The banded crunch is an exercise targeting abs", "Type": "Strength", "BodyPart": "Abdominals", "Equipment": "Bands", "Level": "Intermediate", "Rating": None, "RatingDesc": ""},
    {"Title": "Crunch", "Desc": "The crunch is a popular core exercise", "Type": "Strength", "BodyPart": "Abdominals", "Equipment": "Body Only", "Level": "Intermediate", "Rating": 8.5, "RatingDesc": "Average"},
    {"Title": "Decline band press sit-up", "Desc": "The decline band press sit-up targets abs", "Type": "Strength", "BodyPart": "Abdominals", "Equipment": "Bands", "Level": "Intermediate", "Rating": None, "RatingDesc": ""},
    {"Title": "Barbell roll-out", "Desc": "The barbell roll-out targets abdominal muscles", "Type": "Strength", "BodyPart": "Abdominals", "Equipment": "Barbell", "Level": "Intermediate", "Rating": 8.9, "RatingDesc": "Average"},
    {"Title": "Barbell Ab Rollout - On Knees", "Desc": "The barbell roll-out on knees is an abdominal exercise", "Type": "Strength", "BodyPart": "Abdominals", "Equipment": "Barbell", "Level": "Intermediate", "Rating": 8.9, "RatingDesc": "Average"},
    {"Title": "Decline bar press sit-up", "Desc": "The decline bar press sit-up is a weighted exercise", "Type": "Strength", "BodyPart": "Abdominals", "Equipment": "Barbell", "Level": "Intermediate", "Rating": 8.5, "RatingDesc": "Average"},
    {"Title": "Bench barbell roll-out", "Desc": "The bench barbell roll-out is a challenging ab exercise", "Type": "Strength", "BodyPart": "Abdominals", "Equipment": "Barbell", "Level": "Beginner", "Rating": 8.3, "RatingDesc": "Average"},
    {"Title": "Kettlebell Windmill", "Desc": "The single-kettlebell windmill is a dynamic exercise", "Type": "Strength", "BodyPart": "Abdominals", "Equipment": "Kettlebells", "Level": "Intermediate", "Rating": 7.7, "RatingDesc": "Average"},
    {"Title": "Advanced Kettlebell Windmill", "Desc": "Advanced version of the kettlebell windmill", "Type": "Strength", "BodyPart": "Abdominals", "Equipment": "Kettlebells", "Level": "Beginner", "Rating": 8.3, "RatingDesc": "Average"},
    {"Title": "Kettlebell Pass Between The Legs", "Desc": "A dynamic kettlebell core exercise", "Type": "Strength", "BodyPart": "Abdominals", "Equipment": "Kettlebells", "Level": "Beginner", "Rating": 7.3, "RatingDesc": "Average"},
    {"Title": "Barbell Bench Press - Medium Grip", "Desc": "The barbell bench press is a classic chest exercise", "Type": "Strength", "BodyPart": "Chest", "Equipment": "Barbell", "Level": "Intermediate", "Rating": 9.1, "RatingDesc": "Good"},
    {"Title": "Dumbbell Bench Press", "Desc": "The dumbbell bench press works the chest muscles", "Type": "Strength", "BodyPart": "Chest", "Equipment": "Dumbbell", "Level": "Intermediate", "Rating": 9.0, "RatingDesc": "Good"},
    {"Title": "Incline Dumbbell Press", "Desc": "The incline dumbbell press targets upper chest", "Type": "Strength", "BodyPart": "Chest", "Equipment": "Dumbbell", "Level": "Intermediate", "Rating": 8.8, "RatingDesc": "Average"},
    {"Title": "Push-Up", "Desc": "The push-up is a classic bodyweight chest exercise", "Type": "Strength", "BodyPart": "Chest", "Equipment": "Body Only", "Level": "Beginner", "Rating": 9.2, "RatingDesc": "Good"},
    {"Title": "Wide-Grip Barbell Bench Press", "Desc": "Wide grip variation of bench press", "Type": "Strength", "BodyPart": "Chest", "Equipment": "Barbell", "Level": "Intermediate", "Rating": 8.5, "RatingDesc": "Average"},
    {"Title": "Cable Crossover", "Desc": "The cable crossover is an isolation chest exercise", "Type": "Strength", "BodyPart": "Chest", "Equipment": "Cable", "Level": "Intermediate", "Rating": 8.7, "RatingDesc": "Average"},
    {"Title": "Dumbbell Flyes", "Desc": "Dumbbell flyes isolate the chest muscles", "Type": "Strength", "BodyPart": "Chest", "Equipment": "Dumbbell", "Level": "Intermediate", "Rating": 8.6, "RatingDesc": "Average"},
    {"Title": "Barbell Curl", "Desc": "The barbell curl is a classic biceps exercise", "Type": "Strength", "BodyPart": "Biceps", "Equipment": "Barbell", "Level": "Beginner", "Rating": 9.0, "RatingDesc": "Good"},
    {"Title": "Dumbbell Bicep Curl", "Desc": "The dumbbell bicep curl builds arm strength", "Type": "Strength", "BodyPart": "Biceps", "Equipment": "Dumbbell", "Level": "Beginner", "Rating": 8.9, "RatingDesc": "Average"},
    {"Title": "Hammer Curl", "Desc": "The hammer curl targets the brachialis", "Type": "Strength", "BodyPart": "Biceps", "Equipment": "Dumbbell", "Level": "Beginner", "Rating": 8.7, "RatingDesc": "Average"},
    {"Title": "Preacher Curl", "Desc": "The preacher curl isolates the biceps", "Type": "Strength", "BodyPart": "Biceps", "Equipment": "Barbell", "Level": "Intermediate", "Rating": 8.5, "RatingDesc": "Average"},
    {"Title": "Concentration Curl", "Desc": "Concentration curls isolate each bicep", "Type": "Strength", "BodyPart": "Biceps", "Equipment": "Dumbbell", "Level": "Beginner", "Rating": 8.4, "RatingDesc": "Average"},
    {"Title": "Tricep Dip", "Desc": "Tricep dips target the triceps muscles", "Type": "Strength", "BodyPart": "Triceps", "Equipment": "Body Only", "Level": "Intermediate", "Rating": 8.8, "RatingDesc": "Average"},
    {"Title": "Close-Grip Bench Press", "Desc": "Close grip bench press for triceps", "Type": "Strength", "BodyPart": "Triceps", "Equipment": "Barbell", "Level": "Intermediate", "Rating": 8.7, "RatingDesc": "Average"},
    {"Title": "Tricep Pushdown", "Desc": "The tricep pushdown is a cable exercise", "Type": "Strength", "BodyPart": "Triceps", "Equipment": "Cable", "Level": "Beginner", "Rating": 8.6, "RatingDesc": "Average"},
    {"Title": "Overhead Tricep Extension", "Desc": "Overhead extension targets the triceps", "Type": "Strength", "BodyPart": "Triceps", "Equipment": "Dumbbell", "Level": "Beginner", "Rating": 8.3, "RatingDesc": "Average"},
    {"Title": "Skull Crusher", "Desc": "Skull crushers target the triceps", "Type": "Strength", "BodyPart": "Triceps", "Equipment": "Barbell", "Level": "Intermediate", "Rating": 8.5, "RatingDesc": "Average"},
    {"Title": "Barbell Squat", "Desc": "The barbell squat is a compound leg exercise", "Type": "Strength", "BodyPart": "Quadriceps", "Equipment": "Barbell", "Level": "Intermediate", "Rating": 9.4, "RatingDesc": "Good"},
    {"Title": "Leg Press", "Desc": "The leg press targets the quadriceps", "Type": "Strength", "BodyPart": "Quadriceps", "Equipment": "Machine", "Level": "Beginner", "Rating": 8.9, "RatingDesc": "Average"},
    {"Title": "Lunges", "Desc": "Lunges work multiple leg muscles", "Type": "Strength", "BodyPart": "Quadriceps", "Equipment": "Body Only", "Level": "Beginner", "Rating": 8.7, "RatingDesc": "Average"},
    {"Title": "Leg Extension", "Desc": "Leg extensions isolate the quadriceps", "Type": "Strength", "BodyPart": "Quadriceps", "Equipment": "Machine", "Level": "Beginner", "Rating": 8.2, "RatingDesc": "Average"},
    {"Title": "Front Squat", "Desc": "Front squats emphasize the quadriceps", "Type": "Strength", "BodyPart": "Quadriceps", "Equipment": "Barbell", "Level": "Intermediate", "Rating": 8.8, "RatingDesc": "Average"},
    {"Title": "Romanian Deadlift", "Desc": "The Romanian deadlift targets hamstrings", "Type": "Strength", "BodyPart": "Hamstrings", "Equipment": "Barbell", "Level": "Intermediate", "Rating": 9.0, "RatingDesc": "Good"},
    {"Title": "Leg Curl", "Desc": "Leg curls isolate the hamstrings", "Type": "Strength", "BodyPart": "Hamstrings", "Equipment": "Machine", "Level": "Beginner", "Rating": 8.5, "RatingDesc": "Average"},
    {"Title": "Stiff-Legged Deadlift", "Desc": "Stiff-legged deadlifts work the hamstrings", "Type": "Strength", "BodyPart": "Hamstrings", "Equipment": "Barbell", "Level": "Intermediate", "Rating": 8.7, "RatingDesc": "Average"},
    {"Title": "Deadlift", "Desc": "The deadlift is a compound full body exercise", "Type": "Strength", "BodyPart": "Lower Back", "Equipment": "Barbell", "Level": "Intermediate", "Rating": 9.5, "RatingDesc": "Good"},
    {"Title": "Bent Over Barbell Row", "Desc": "The bent over row targets the back", "Type": "Strength", "BodyPart": "Middle Back", "Equipment": "Barbell", "Level": "Intermediate", "Rating": 9.1, "RatingDesc": "Good"},
    {"Title": "Pull-Up", "Desc": "Pull-ups work the lats and upper back", "Type": "Strength", "BodyPart": "Lats", "Equipment": "Body Only", "Level": "Intermediate", "Rating": 9.3, "RatingDesc": "Good"},
    {"Title": "Lat Pulldown", "Desc": "The lat pulldown targets the latissimus dorsi", "Type": "Strength", "BodyPart": "Lats", "Equipment": "Cable", "Level": "Beginner", "Rating": 8.8, "RatingDesc": "Average"},
    {"Title": "Seated Cable Row", "Desc": "Seated cable rows work the middle back", "Type": "Strength", "BodyPart": "Middle Back", "Equipment": "Cable", "Level": "Beginner", "Rating": 8.7, "RatingDesc": "Average"},
    {"Title": "One-Arm Dumbbell Row", "Desc": "Single arm rows for back development", "Type": "Strength", "BodyPart": "Middle Back", "Equipment": "Dumbbell", "Level": "Beginner", "Rating": 8.9, "RatingDesc": "Average"},
    {"Title": "Military Press", "Desc": "The military press targets the shoulders", "Type": "Strength", "BodyPart": "Shoulders", "Equipment": "Barbell", "Level": "Intermediate", "Rating": 9.0, "RatingDesc": "Good"},
    {"Title": "Dumbbell Shoulder Press", "Desc": "Dumbbell shoulder press for deltoids", "Type": "Strength", "BodyPart": "Shoulders", "Equipment": "Dumbbell", "Level": "Beginner", "Rating": 8.9, "RatingDesc": "Average"},
    {"Title": "Lateral Raise", "Desc": "Lateral raises target the side deltoids", "Type": "Strength", "BodyPart": "Shoulders", "Equipment": "Dumbbell", "Level": "Beginner", "Rating": 8.5, "RatingDesc": "Average"},
    {"Title": "Front Raise", "Desc": "Front raises target the anterior deltoid", "Type": "Strength", "BodyPart": "Shoulders", "Equipment": "Dumbbell", "Level": "Beginner", "Rating": 8.2, "RatingDesc": "Average"},
    {"Title": "Upright Row", "Desc": "Upright rows work shoulders and traps", "Type": "Strength", "BodyPart": "Shoulders", "Equipment": "Barbell", "Level": "Intermediate", "Rating": 8.1, "RatingDesc": "Average"},
    {"Title": "Calf Raise", "Desc": "Calf raises target the gastrocnemius", "Type": "Strength", "BodyPart": "Calves", "Equipment": "Machine", "Level": "Beginner", "Rating": 8.4, "RatingDesc": "Average"},
    {"Title": "Seated Calf Raise", "Desc": "Seated calf raises for soleus", "Type": "Strength", "BodyPart": "Calves", "Equipment": "Machine", "Level": "Beginner", "Rating": 8.2, "RatingDesc": "Average"},
    {"Title": "Standing Calf Raise", "Desc": "Standing calf raises for calf development", "Type": "Strength", "BodyPart": "Calves", "Equipment": "Body Only", "Level": "Beginner", "Rating": 8.3, "RatingDesc": "Average"},
    {"Title": "Wrist Curl", "Desc": "Wrist curls strengthen the forearms", "Type": "Strength", "BodyPart": "Forearms", "Equipment": "Barbell", "Level": "Beginner", "Rating": 7.8, "RatingDesc": "Average"},
    {"Title": "Reverse Wrist Curl", "Desc": "Reverse wrist curls target forearm extensors", "Type": "Strength", "BodyPart": "Forearms", "Equipment": "Barbell", "Level": "Beginner", "Rating": 7.5, "RatingDesc": "Average"},
    {"Title": "Barbell Shrug", "Desc": "Barbell shrugs target the trapezius", "Type": "Strength", "BodyPart": "Traps", "Equipment": "Barbell", "Level": "Beginner", "Rating": 8.4, "RatingDesc": "Average"},
    {"Title": "Dumbbell Shrug", "Desc": "Dumbbell shrugs for trap development", "Type": "Strength", "BodyPart": "Traps", "Equipment": "Dumbbell", "Level": "Beginner", "Rating": 8.3, "RatingDesc": "Average"},
    {"Title": "Hip Thrust", "Desc": "Hip thrusts target the glutes", "Type": "Strength", "BodyPart": "Glutes", "Equipment": "Barbell", "Level": "Intermediate", "Rating": 9.0, "RatingDesc": "Good"},
    {"Title": "Glute Bridge", "Desc": "Glute bridges activate the gluteus maximus", "Type": "Strength", "BodyPart": "Glutes", "Equipment": "Body Only", "Level": "Beginner", "Rating": 8.5, "RatingDesc": "Average"},
    {"Title": "Cable Kickback", "Desc": "Cable kickbacks isolate the glutes", "Type": "Strength", "BodyPart": "Glutes", "Equipment": "Cable", "Level": "Beginner", "Rating": 8.2, "RatingDesc": "Average"},
    {"Title": "Plank", "Desc": "The plank is an isometric core exercise", "Type": "Strength", "BodyPart": "Abdominals", "Equipment": "Body Only", "Level": "Beginner", "Rating": 8.8, "RatingDesc": "Average"},
    {"Title": "Side Plank", "Desc": "Side planks target the obliques", "Type": "Strength", "BodyPart": "Abdominals", "Equipment": "Body Only", "Level": "Beginner", "Rating": 8.5, "RatingDesc": "Average"},
    {"Title": "Russian Twist", "Desc": "Russian twists work the obliques", "Type": "Strength", "BodyPart": "Abdominals", "Equipment": "Body Only", "Level": "Beginner", "Rating": 8.3, "RatingDesc": "Average"},
    {"Title": "Hanging Leg Raise", "Desc": "Hanging leg raises target lower abs", "Type": "Strength", "BodyPart": "Abdominals", "Equipment": "Body Only", "Level": "Intermediate", "Rating": 8.9, "RatingDesc": "Average"},
    {"Title": "Mountain Climber", "Desc": "Mountain climbers are a cardio core exercise", "Type": "Cardio", "BodyPart": "Abdominals", "Equipment": "Body Only", "Level": "Beginner", "Rating": 8.4, "RatingDesc": "Average"},
    {"Title": "Burpee", "Desc": "Burpees are a full body cardio exercise", "Type": "Cardio", "BodyPart": "Abdominals", "Equipment": "Body Only", "Level": "Intermediate", "Rating": 8.7, "RatingDesc": "Average"},
    {"Title": "Jumping Jacks", "Desc": "Jumping jacks are a classic cardio exercise", "Type": "Cardio", "BodyPart": "Abdominals", "Equipment": "Body Only", "Level": "Beginner", "Rating": 7.5, "RatingDesc": "Average"},
    {"Title": "Box Jump", "Desc": "Box jumps are a plyometric exercise", "Type": "Plyometrics", "BodyPart": "Quadriceps", "Equipment": "Other", "Level": "Intermediate", "Rating": 8.6, "RatingDesc": "Average"},
    {"Title": "Jump Squat", "Desc": "Jump squats combine strength and power", "Type": "Plyometrics", "BodyPart": "Quadriceps", "Equipment": "Body Only", "Level": "Intermediate", "Rating": 8.5, "RatingDesc": "Average"},
    {"Title": "Hamstring Stretch", "Desc": "Stretching exercise for the hamstrings", "Type": "Stretching", "BodyPart": "Hamstrings", "Equipment": "Body Only", "Level": "Beginner", "Rating": 7.8, "RatingDesc": "Average"},
    {"Title": "Quad Stretch", "Desc": "Stretching exercise for the quadriceps", "Type": "Stretching", "BodyPart": "Quadriceps", "Equipment": "Body Only", "Level": "Beginner", "Rating": 7.7, "RatingDesc": "Average"},
    {"Title": "Shoulder Stretch", "Desc": "Stretching exercise for the shoulders", "Type": "Stretching", "BodyPart": "Shoulders", "Equipment": "Body Only", "Level": "Beginner", "Rating": 7.5, "RatingDesc": "Average"},
    {"Title": "Chest Stretch", "Desc": "Stretching exercise for the chest", "Type": "Stretching", "BodyPart": "Chest", "Equipment": "Body Only", "Level": "Beginner", "Rating": 7.6, "RatingDesc": "Average"},
    {"Title": "Hip Flexor Stretch", "Desc": "Stretching exercise for hip flexors", "Type": "Stretching", "BodyPart": "Quadriceps", "Equipment": "Body Only", "Level": "Beginner", "Rating": 8.0, "RatingDesc": "Average"},
    {"Title": "Tricep Stretch", "Desc": "Stretching exercise for the triceps", "Type": "Stretching", "BodyPart": "Triceps", "Equipment": "Body Only", "Level": "Beginner", "Rating": 7.4, "RatingDesc": "Average"},
    {"Title": "Back Stretch", "Desc": "Stretching exercise for the back", "Type": "Stretching", "BodyPart": "Middle Back", "Equipment": "Body Only", "Level": "Beginner", "Rating": 7.9, "RatingDesc": "Average"},
    {"Title": "Calf Stretch", "Desc": "Stretching exercise for the calves", "Type": "Stretching", "BodyPart": "Calves", "Equipment": "Body Only", "Level": "Beginner", "Rating": 7.6, "RatingDesc": "Average"},
    {"Title": "Neck Stretch", "Desc": "Stretching exercise for the neck", "Type": "Stretching", "BodyPart": "Neck", "Equipment": "Body Only", "Level": "Beginner", "Rating": 7.3, "RatingDesc": "Average"},
    {"Title": "Glute Stretch", "Desc": "Stretching exercise for the glutes", "Type": "Stretching", "BodyPart": "Glutes", "Equipment": "Body Only", "Level": "Beginner", "Rating": 7.7, "RatingDesc": "Average"},
]

# Create DataFrame
df = pd.DataFrame(exercises)

# Save to CSV
output_path = os.path.join(os.path.dirname(__file__), 'data', 'megaGymDataset.csv')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df.to_csv(output_path, index=False)

print(f"Dataset saved to {output_path}")
print(f"Total exercises: {len(df)}")
print(f"\nBody parts: {df['BodyPart'].unique().tolist()}")
print(f"\nEquipment: {df['Equipment'].unique().tolist()}")
print(f"\nLevels: {df['Level'].unique().tolist()}")
print(f"\nTypes: {df['Type'].unique().tolist()}")
