"""Everything Reel knows about Kirran Suleman.

Edit PROFILE below whenever the portfolio changes. The chatbot is told to answer
only from this data, so anything you add here becomes something it can talk about.
"""

BOT_NAME = "Reel"
PORTFOLIO_URL = "https://kirransuleman-portfolio.netlify.app"

PROFILE = {
    "name": "Kirran Suleman",
    "title": "Content creator and digital media producer",
    "tagline": "I make products move.",
    "summary": (
        "Kirran edits, animates and art-directs video for Korean skincare and "
        "beauty brands, from AI UGC ads to motion graphics that make a product "
        "feel as good as it looks."
    ),
    "skills": {
        "Video editing and design": (
            "Social-first edits and layouts built in CapCut and Canva, "
            "finished with Adobe Creative Suite."
        ),
        "Motion and 3D": (
            "Motion graphics and animation in Adobe tools, plus 3D modeling "
            "and animation in Blender."
        ),
        "Post-production": (
            "Professional editing and colour grading in DaVinci Resolve for a "
            "clean, cinematic finish."
        ),
    },
    "tools": [
        "CapCut",
        "Canva",
        "Adobe Creative Suite",
        "DaVinci Resolve",
        "Blender",
    ],
    "specialties": [
        "AI UGC video creation",
        "Skincare product advertising",
        "AI product animation",
        "Creative video editing",
        "Visual storytelling",
        "Social media ad creation",
        "Motion graphics",
        "Colour grading",
    ],
    "creative_work": [
        "Product advertisement and motion graphics: products brought to life through animation",
        "Kinetic typography and text animation: type that moves with the message",
        "Social media promotional and marketing videos: made for feeds and short-form",
        "Logo animation and brand identity motion design: identity systems in motion",
        "Professional video editing and post-production: edit, grade and deliver",
    ],
    "experience": {
        "role": "AI UGC ad creator for Korean skincare and beauty",
        "description": (
            "Creates AI-powered, UGC-style advertisement videos for Korean "
            "skincare and beauty brands: aesthetic, engaging product "
            "commercials made for social media platforms."
        ),
        "projects": [
            {
                "brand": "Ongredients",
                "type": "Skin barrier product ad",
                "details": [
                    "Created AI-powered skincare product promotional videos.",
                    "Focused on skin barrier care and product presentation.",
                ],
            },
            {
                "brand": "Suiskin",
                "type": "Vegan skincare UGC ad",
                "details": [
                    "Developed aesthetic vegan skincare advertisement concepts.",
                    "Created natural-looking product visuals and engaging scenes.",
                ],
            },
            {
                "brand": "Baegayul",
                "type": "Calming skincare product ad",
                "details": [
                    "Designed calming and minimalist skincare promotional videos.",
                    "Used soft visuals and cinematic product animations.",
                ],
            },
            {
                "brand": "FREEMAY",
                "type": "Beauty product promotional video",
                "details": [
                    "Created attractive AI-generated beauty product advertisements.",
                    "Focused on creative storytelling and social media engagement.",
                ],
            },
        ],
    },
    "education": {
        "academic": "BBA",
        "professional_training": "Video editing and content creation",
        "technical_skills": "Motion graphics, graphic design, video editing and 3D animation",
        "software": "CapCut, Canva, Adobe Creative Suite, Blender and DaVinci Resolve",
    },
    "contact": (
        "Visitors can reach Kirran through the contact form at the bottom of the "
        f"portfolio ({PORTFOLIO_URL}/#contact). The form asks for name, email and "
        "a message about the product and where the video will run."
    ),
}


def _format_profile(p: dict) -> str:
    lines = [
        f"Name: {p['name']}",
        f"Title: {p['title']}",
        f"Tagline: \"{p['tagline']}\"",
        f"About: {p['summary']}",
        "",
        "SKILLS",
    ]
    lines += [f"- {k}: {v}" for k, v in p["skills"].items()]
    lines += ["", "TOOLS: " + ", ".join(p["tools"])]
    lines += ["SPECIALTIES: " + ", ".join(p["specialties"])]
    lines += ["", "PROJECTS AND CREATIVE WORK"]
    lines += [f"- {item}" for item in p["creative_work"]]

    exp = p["experience"]
    lines += ["", f"EXPERIENCE: {exp['role']}", exp["description"], "Selected brand concept projects:"]
    for proj in exp["projects"]:
        lines.append(f"- {proj['brand']} ({proj['type']}): " + " ".join(proj["details"]))

    edu = p["education"]
    lines += [
        "",
        "EDUCATION AND QUALIFICATIONS",
        f"- Academic qualification: {edu['academic']}",
        f"- Professional training: {edu['professional_training']}",
        f"- Technical skills: {edu['technical_skills']}",
        f"- Software proficiency: {edu['software']}",
        "",
        "CONTACT",
        p["contact"],
    ]
    return "\n".join(lines)


SYSTEM_PROMPT = f"""You are {BOT_NAME}, the AI assistant on {PROFILE['name']}'s portfolio website ({PORTFOLIO_URL}).
You help visitors (brand owners, marketers, recruiters, collaborators) learn about {PROFILE['name']}'s skills, projects, experience, education and how to get in touch.

Rules:
- Answer ONLY from the profile below. Never invent clients, results, prices, turnaround times, years of experience, rates, email addresses, phone numbers or social links.
- If something is not in the profile, say you don't have that detail and suggest the contact form on the portfolio ({PORTFOLIO_URL}/#contact).
- Speak about {PROFILE['name']} in the third person. You are an assistant, not Kirran.
- Be warm, professional and concise: usually 2 to 5 short sentences. Use short bullet lists (lines starting with "- ") only when listing several items.
- When someone describes a product or campaign, say which of Kirran's skills and past work fit it, and invite them to use the contact form.
- Stay on topic. Politely decline unrelated requests (coding help, homework, politics) and steer back to Kirran's work.
- Reply in the language the visitor writes in.

PROFILE
{_format_profile(PROFILE)}
"""
