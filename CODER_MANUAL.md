# Phillips Curve Classification - Coder Manual

## Welcome

You've been asked to help validate AI-generated classifications of FOMC (Federal Open Market Committee) transcript statements. This manual will walk you through everything you need to do.

**Good news:** You don't need to install anything. The tool runs in your web browser.

---

## Quick Start (5 minutes)

### Step 1: Open the Tool

Click this link or copy it into your browser:

**https://llmhumancodeweb-9scksmewtetcjowbyvyjsr.streamlit.app/**

The page may take 10-30 seconds to load the first time (the server "wakes up" if no one has used it recently).

### Step 2: Enter Your Name

1. Look at the **left sidebar** (on mobile, tap the `>` arrow in the top-left corner)
2. Type your name in the "Your Name" field
3. Your name will be locked after your first save to keep your data consistent

### Step 3: Select Data Source

1. Keep **"Use default sample"** selected (this loads the 200 arguments you need to code)
2. You should see "Loaded 200 arguments" in green

### Step 4: Start Coding

You're ready to go! See the "How to Code" section below.

---

## How to Code

### What You'll See

For each argument, you'll see:

| Section | What It Shows |
|---------|---------------|
| **Quotation** | The actual quote from an FOMC meeting transcript |
| **Description** | A short summary of what the speaker is saying |
| **Explanation** | The policy context or interpretation |
| **Economic Variable** | Whether this relates to Growth, Inflation, or Employment |

### Your Task

**Question:** Does this speaker express a belief about how labor market conditions affect inflation?

This is called the "Phillips curve" relationship - the idea that tight labor markets (low unemployment) cause higher inflation.

### Classification Options

Choose ONE of these four options:

| Option | When to Use It |
|--------|----------------|
| **STEEP** | Speaker says labor markets SIGNIFICANTLY affect inflation. Look for: "drives", "causes", "leads to", "will feed into" |
| **FLAT** | Speaker says labor markets have LITTLE or NO effect on inflation. Look for: "despite tight labor...", "hasn't translated", "no longer valid" |
| **MODERATE** | Speaker indicates a QUALIFIED or PARTIAL relationship. Look for: "some", "modest", "limited" |
| **NONE** | No Phillips curve belief expressed. Use this when the quote mentions labor OR inflation but not both, or mentions both with no causal claim |

**Tip:** Click the "Classification Guide" expander on the right side for examples.

### Saving Your Work

1. Select your classification
2. (Optional) Add notes if something seems unclear or ambiguous
3. Click **"Save & Continue"** - this saves your answer AND moves to the next argument
4. Use **"Skip"** if you want to come back to an argument later
5. Use **"Previous"** to go back and review/change previous answers

---

## IMPORTANT: Downloading Your Results

**The website does NOT permanently save your work.** You must download your results before closing your browser.

### How to Download

1. Look at the left sidebar
2. Find the **"Save Results"** section
3. Click **"Download Results CSV"**
4. Save the file somewhere you can find it (like your Desktop or Documents folder)
5. The filename will look like: `coded_yourname_phillips_20241215_143022.csv`

### When to Download

- **Before closing your browser tab**
- **Before your computer goes to sleep** (if you'll be away for a while)
- **Periodically** as you work (every 20-30 arguments is a good habit)
- **When you're done** for the day

---

## Taking a Break / Resuming Later

### Ending a Session

1. Download your results CSV (see above)
2. Close the browser tab
3. Keep your CSV file safe

### Resuming Your Work

1. Go back to: **https://llmhumancodeweb-9scksmewtetcjowbyvyjsr.streamlit.app/**
2. Enter your name in the sidebar
3. Scroll down in the sidebar to find **"Resume Session"**
4. Click **"Browse files"** and select your previously downloaded CSV
5. Click **"Load Session"**
6. You'll automatically jump to where you left off

**Note:** Always use your most recent CSV file when resuming.

---

## Submitting Your Final Results

When you've finished coding all 200 arguments:

1. Download your final results CSV
2. Email the CSV file to: **[Ask your supervisor for the email address]**
3. Or upload to the shared folder: **[Ask your supervisor for the folder location]**

---

## Troubleshooting

### "The page won't load"

- Wait 30 seconds - the server may be starting up
- Try refreshing the page (Ctrl+R or Cmd+R)
- Try a different browser (Chrome, Firefox, Safari, Edge all work)

### "I accidentally closed my browser and didn't download"

- Unfortunately, your progress is lost if you didn't download
- This is why downloading regularly is important
- Start again and work through the arguments

### "The page looks weird on my phone"

- The tool works best on a computer/laptop
- On mobile, tap the `>` arrow in the top-left to see the sidebar

### "I made a mistake on a previous argument"

- Use the **"Previous"** button to go back
- Or use the **"Jump to"** box to go to a specific argument number
- Change your answer and click **"Save & Continue"**

### "I'm not sure which classification to pick"

- When in doubt, use **NONE** (it's the default)
- Add a note explaining your uncertainty
- The research team will review edge cases

---

## Example Walkthrough

Here's what a typical coding session looks like:

1. **Open the link** - https://llmhumancodeweb-9scksmewtetcjowbyvyjsr.streamlit.app/
2. **Enter name** - "John Smith"
3. **See Argument 1** - Read the quotation about inflation expectations
4. **Decide** - This speaker says "tight labor markets will feed into wage pressures" - that sounds like STEEP
5. **Select STEEP** and click **Save & Continue**
6. **See Argument 2** - Continue...
7. **After 30 arguments** - Click "Download Results CSV" to save progress
8. **Continue coding...**
9. **Need a break** - Download CSV, close browser
10. **Next day** - Open link, enter name, upload CSV in "Resume Session", click "Load Session"
11. **Continue from where you left off**
12. **Finish all 200** - Download final CSV, email to research team

---

## Quick Reference Card

| Action | How To Do It |
|--------|--------------|
| **Open tool** | Go to https://llmhumancodeweb-9scksmewtetcjowbyvyjsr.streamlit.app/ |
| **Save answer** | Click "Save & Continue" |
| **Skip argument** | Click "Skip" |
| **Go back** | Click "Previous" or use "Jump to" |
| **Download results** | Sidebar > "Download Results CSV" |
| **Resume session** | Sidebar > "Resume Session" > Upload CSV > "Load Session" |
| **See help** | Click "Classification Guide" expander |

---

## Questions?

Contact the research team if you have questions about:
- What a specific argument means
- Which classification to choose for edge cases
- Technical problems with the website

Thank you for your help with this research project!
