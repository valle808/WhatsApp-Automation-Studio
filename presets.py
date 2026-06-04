#!/usr/bin/env python3
"""
presets.py — WhatsApp Campaign Studio
60 diverse message templates across 12 categories.
"""
import json
import os

PRESETS_PATH = os.path.expanduser("~/whatsapp_campaign_presets.json")

DEFAULT_PRESETS = [
    # ── 1. PRANKS / FUN ──────────────────────────────────────────────────────
    {
        "name": "🎭 Invisible Bomb",
        "message": "ㅤ" * 200,
        "description": "200 invisible characters — creates a scroll 'bomb' effect"
    },
    {
        "name": "🎭 Help Prank",
        "messages": ["ㅤ", "HELP ME", "ㅤ", "ㅤ", "PLEASE"],
        "description": "Random invisible + HELP ME messages (set repeat high)"
    },
    {
        "name": "🎭 Ghost Typing",
        "messages": ["...", "…", "I need to tell you something", "…", "Never mind"],
        "description": "Creates suspense before saying nothing"
    },
    {
        "name": "🎭 Emoji Flood",
        "message": "😂" * 50 + "\n" + "💀" * 50,
        "description": "Sends a wall of laughing + skull emojis"
    },
    {
        "name": "🎭 Reverse Psychology",
        "messages": [
            "Don't open this message",
            "I said don't look",
            "Why are you still reading?",
            "Seriously stop it",
            "Fine. Hi. 👋"
        ],
        "description": "Curiosity-driven prank sequence"
    },

    # ── 2. LOVE & ROMANCE ────────────────────────────────────────────────────
    {
        "name": "❤️ Simple Love",
        "messages": [
            "I love you ❤️", "Miss you so much 💕", "You're my everything 🌹",
            "Thinking of you 💭", "Can't wait to see you again 🤗",
            "You make me smile every day 😊", "Forever yours 💖"
        ],
        "description": "Short sweet love messages"
    },
    {
        "name": "❤️ Good Morning Love",
        "messages": [
            "Good morning beautiful ☀️ I was thinking of you the moment I woke up!",
            "Rise and shine love! Hope your day is as wonderful as you are 🌸",
            "Good morning! You are the reason I smile every morning 😊💕",
            "Morning sunshine! Wishing you the most amazing day ✨"
        ],
        "description": "Romantic good morning messages"
    },
    {
        "name": "❤️ Good Night Love",
        "messages": [
            "Good night my love 🌙 Sweet dreams 💭",
            "Wishing you the sweetest dreams tonight ⭐",
            "Sleep tight, thinking of you 🌛❤️",
            "Good night! Tomorrow I'll get to talk to you again — can't wait 😊"
        ],
        "description": "Romantic good night messages"
    },
    {
        "name": "❤️ Anniversary Special",
        "messages": [
            "Happy Anniversary! 🎉 Every day with you is a gift I treasure ❤️",
            "On this special day, I want you to know how much you mean to me 💕",
            "Another year of us. Best year yet. 🥂❤️",
            "You are my greatest adventure. Happy Anniversary! 🌹"
        ],
        "description": "Anniversary celebration messages"
    },
    {
        "name": "❤️ Miss You",
        "messages": [
            "I miss you more than words can say 💔",
            "The house feels empty without you 🏠",
            "Can't wait until we're together again 🤗",
            "Every moment apart feels like forever 💭",
            "Distance means nothing when someone means everything ❤️"
        ],
        "description": "Heartfelt 'I miss you' messages"
    },

    # ── 3. GOOD MORNING ───────────────────────────────────────────────────────
    {
        "name": "☀️ Good Morning (General)",
        "messages": [
            "Good morning! Hope your day is amazing ☀️",
            "Rise and shine! Sending you positive vibes 🌟",
            "Morning! A new day, a fresh start 🌅",
            "Good morning! Today is going to be a great day 💪",
            "Wake up and be awesome! Good morning! 😊"
        ],
        "description": "Energetic general good morning messages"
    },
    {
        "name": "☀️ Monday Motivation",
        "messages": [
            "Happy Monday! Let's make this week incredible! 💼🔥",
            "New week, new goals, new achievements! Good morning! 🎯",
            "Monday is just a day, your attitude makes it great! ☀️",
            "Coffee in hand, goals in mind — let's crush this Monday! ☕💪"
        ],
        "description": "Monday morning motivation boosts"
    },
    {
        "name": "☀️ Weekend Vibes",
        "messages": [
            "Happy Friday! The weekend is almost here 🎉",
            "It's finally Friday! Time to relax and recharge! 🥳",
            "TGIF! Have an amazing weekend! 🌴",
            "Weekend mode: ON 🎮🛋️ Enjoy every second!"
        ],
        "description": "Friday/weekend celebration messages"
    },

    # ── 4. BUSINESS & MARKETING ───────────────────────────────────────────────
    {
        "name": "💼 Flash Sale Announcement",
        "messages": [
            "🔥 FLASH SALE! 50% OFF everything for the next 24 hours only! Don't miss out — shop now!",
            "⚡ LIMITED TIME OFFER! Grab your favorites at half price. Sale ends midnight! 🛒",
            "🎁 SPECIAL DEAL ALERT! Use code SAVE50 for 50% off your order today only!"
        ],
        "description": "Urgent flash sale promotional messages"
    },
    {
        "name": "💼 New Product Launch",
        "messages": [
            "🚀 BIG NEWS! We just launched something incredible. Be the first to check it out! 👀",
            "🎉 It's here! Our brand new product is now available. Click to see what all the buzz is about!",
            "💥 JUST DROPPED! You've been waiting for this — and it's finally here! Limited stock available."
        ],
        "description": "Product launch announcement templates"
    },
    {
        "name": "💼 Appointment Reminder",
        "messages": [
            "Hi! This is a friendly reminder that your appointment is scheduled for tomorrow. See you soon! 📅",
            "Reminder: Don't forget your appointment with us! Please arrive 10 minutes early. 🕐",
            "Your appointment is coming up! Reply YES to confirm or call us to reschedule. 📞"
        ],
        "description": "Professional appointment reminder messages"
    },
    {
        "name": "💼 Customer Thank You",
        "messages": [
            "Thank you for your purchase! We truly appreciate your support 🙏 Your order is on its way!",
            "We're so grateful for your business! Don't hesitate to reach out if you need anything 😊",
            "Thank you! We hope you love your order. Leave us a review — it means the world to us! ⭐"
        ],
        "description": "Customer appreciation messages"
    },
    {
        "name": "💼 Follow-up Message",
        "messages": [
            "Hi! Just checking in to see if you had any questions about our last conversation 😊",
            "Following up on my previous message — hope to hear from you soon! 🤝",
            "Just a quick follow-up! We'd love to help you out. What can we do for you? 💬"
        ],
        "description": "Professional follow-up messages"
    },
    {
        "name": "💼 Review Request",
        "messages": [
            "Hi! We hope you're loving your purchase 🛍️ Would you mind leaving us a quick review? It helps us a lot! ⭐",
            "Your feedback matters! Drop us a review and let us know how we did 🙏",
            "Quick favor — could you leave a 5-star review? Takes 30 seconds and means the world to us! 🌟"
        ],
        "description": "Polite review/feedback request messages"
    },

    # ── 5. EVENTS & INVITATIONS ───────────────────────────────────────────────
    {
        "name": "🎉 Party Invitation",
        "messages": [
            "🎉 YOU'RE INVITED! Join us for an epic party — Date: [DATE], Time: [TIME], Place: [VENUE]. RSVP NOW!",
            "It's party time! 🥳 We'd love to see you there. Confirm your attendance by [DATE]!",
            "Save the date! 📅 We're celebrating and YOU need to be there! Details coming soon 🎊"
        ],
        "description": "Party and social event invitations"
    },
    {
        "name": "🎉 Birthday Wishes",
        "messages": [
            "🎂 Happy Birthday! Wishing you a day as wonderful as you are! 🎉",
            "Happy Birthday! 🎈 Hope this year brings you everything you've dreamed of! 🌟",
            "Many happy returns of the day! 🎂 You deserve all the cake and happiness! 😊🎊",
            "Happy Birthday! May your day be full of joy, laughter, and love! 🥳❤️"
        ],
        "description": "Birthday celebration messages"
    },
    {
        "name": "🎉 Wedding Congratulations",
        "messages": [
            "Congratulations on your wedding! 💍 Wishing you a lifetime of love and happiness! 💕",
            "Best wishes to the happy couple! 🥂 Here's to a beautiful journey together!",
            "Congrats! May your marriage be filled with laughter, love, and adventure! 🌹"
        ],
        "description": "Wedding congratulations messages"
    },
    {
        "name": "🎉 Graduation Congratulations",
        "messages": [
            "🎓 Congratulations Graduate! All your hard work paid off — you did it! 🙌",
            "You made it! 🎓 So proud of everything you've achieved. The world is yours!",
            "Congrats on your graduation! 🎉 This is just the beginning of an amazing chapter! 🌟"
        ],
        "description": "Graduation celebration messages"
    },
    {
        "name": "🎉 New Year Wishes",
        "messages": [
            "🎆 Happy New Year! May the coming year bring you joy, success, and all your heart desires! 🥂",
            "Wishing you a fabulous New Year! Out with the old, in with the amazing! 🎇✨",
            "New year, new opportunities! 🎉 Hope this year is your best one yet! 🌟"
        ],
        "description": "New Year celebration messages"
    },
    {
        "name": "🎉 Christmas & Holiday",
        "messages": [
            "🎄 Merry Christmas! Wishing you a holiday filled with warmth, joy, and love! 🎁",
            "Happy Holidays! 🎅 Hope this festive season brings you lots of cheer and happiness! ✨",
            "Season's Greetings! 🎊 Wishing you and your loved ones a magical holiday! 🦌❄️"
        ],
        "description": "Christmas and holiday greetings"
    },

    # ── 6. MOTIVATION & INSPIRATION ───────────────────────────────────────────
    {
        "name": "💪 Daily Motivation",
        "messages": [
            "You are capable of amazing things! Believe in yourself today 💪",
            "Every day is a new opportunity to grow. Make it count! 🌱",
            "Push through. You're closer to your goal than you think! 🎯",
            "Don't give up. Great things take time ⏰ Keep going! 🔥",
            "The only limit is the one you set yourself. Aim higher! 🚀"
        ],
        "description": "Daily motivational messages"
    },
    {
        "name": "💪 Gym & Fitness",
        "messages": [
            "💪 No pain, no gain! Time to hit the gym and crush those goals!",
            "Gym time! 🏋️ Every rep gets you closer to the best version of yourself!",
            "Rise up, show up, and never give up! It's workout time! 🔥",
            "Your future self will thank you for today's workout! Let's go! 💪🏃"
        ],
        "description": "Fitness and workout motivation messages"
    },
    {
        "name": "💪 Success Quotes",
        "messages": [
            "\"Success is not final, failure is not fatal: It is the courage to continue that counts.\" – Churchill",
            "\"The only way to do great work is to love what you do.\" – Steve Jobs",
            "\"It always seems impossible until it's done.\" – Nelson Mandela",
            "\"Believe you can and you're halfway there.\" – Theodore Roosevelt"
        ],
        "description": "Famous motivational quotes"
    },

    # ── 7. CUSTOMER SUPPORT ───────────────────────────────────────────────────
    {
        "name": "🛎️ Welcome Message",
        "messages": [
            "👋 Hello! Welcome to [Business Name]! How can we help you today?",
            "Hi there! Thanks for reaching out to us 😊 What can we do for you?",
            "Welcome! We're happy you contacted us. Our team is here to assist you! 🙌"
        ],
        "description": "Customer service welcome/greeting messages"
    },
    {
        "name": "🛎️ Order Confirmation",
        "messages": [
            "✅ Your order has been confirmed! Order #[NUMBER]. Expected delivery: [DATE]. Thank you! 📦",
            "Great news! Your order is confirmed and being processed. We'll notify you when it ships! 🚚",
            "Order confirmed! 🎉 We're packing it up now. Get ready to receive your goodies!"
        ],
        "description": "Order confirmation messages"
    },
    {
        "name": "🛎️ Shipping Notification",
        "messages": [
            "📦 Your order has shipped! Track it here: [TRACKING_LINK]. Estimated arrival: [DATE]",
            "Great news! Your package is on its way 🚚 Track your order with code: [TRACKING]",
            "Your order is out for delivery today! 🏠 Keep an eye out for the delivery person! 📬"
        ],
        "description": "Shipping and delivery notification messages"
    },
    {
        "name": "🛎️ Support Closing",
        "messages": [
            "Thank you for contacting us! Your issue has been resolved. Don't hesitate to reach out again 😊",
            "We hope we were able to help! If you need anything else, we're just a message away! 🙏",
            "Thanks for your patience! Let us know if there's anything else we can assist you with ✅"
        ],
        "description": "Customer support closing messages"
    },

    # ── 8. HEALTH & WELLNESS ──────────────────────────────────────────────────
    {
        "name": "🌿 Wellness Check-in",
        "messages": [
            "Hey! Just checking in on you 💚 How are you feeling today?",
            "Hi! Don't forget to take care of yourself today 🌸 You matter!",
            "Just a reminder: drink water, breathe, and be kind to yourself today 💧🌿"
        ],
        "description": "Friendly wellness check-in messages"
    },
    {
        "name": "🌿 Medication Reminder",
        "messages": [
            "💊 Time to take your medication! Stay healthy! ❤️",
            "Medication reminder! Don't forget to take your pills today 🕐💊",
            "Health reminder: time for your daily medication! 🌡️"
        ],
        "description": "Medical/medication reminder messages"
    },
    {
        "name": "🌿 Hydration Reminder",
        "messages": [
            "💧 Don't forget to drink water! Stay hydrated and healthy! 🌊",
            "Water reminder! 💦 Have you had enough water today? Your body will thank you!",
            "Hydration check! 💧 Time to drink a glass of water 🥤"
        ],
        "description": "Daily hydration reminder messages"
    },

    # ── 9. EDUCATION ──────────────────────────────────────────────────────────
    {
        "name": "📚 Study Group Invite",
        "messages": [
            "📚 Study session at [PLACE] on [DATE] at [TIME]! Come prepared — we're covering [TOPIC] 💡",
            "Hey! Don't forget our study group meeting tomorrow 📖 Bring your notes!",
            "Study group reminder! 🎓 See you all at [TIME] in [LOCATION] — let's ace this! 💪"
        ],
        "description": "Study group coordination messages"
    },
    {
        "name": "📚 Assignment Reminder",
        "messages": [
            "⏰ REMINDER: Assignment due tomorrow! Don't forget to submit on time 📝",
            "Quick reminder — your [SUBJECT] assignment is due on [DATE]. Get it done! ✅",
            "Don't forget: project submission deadline is [DATE]! Last chance to submit! 📚"
        ],
        "description": "Academic assignment deadline reminders"
    },
    {
        "name": "📚 Class Cancelled Notice",
        "messages": [
            "📢 NOTICE: Today's [SUBJECT] class at [TIME] has been cancelled. See you next time!",
            "Class update: [SUBJECT] is cancelled today. Check the portal for rescheduled date 📅",
            "Heads up! [PROFESSOR]'s class won't be held today. Enjoy the free time! 🎉"
        ],
        "description": "Class cancellation notification messages"
    },

    # ── 10. SOCIAL & COMMUNITY ────────────────────────────────────────────────
    {
        "name": "🤝 Group Welcome",
        "messages": [
            "👋 Welcome to the group [NAME]! Great to have you here! 🎉",
            "Welcome aboard [NAME]! 🙌 Feel free to introduce yourself!",
            "Hi [NAME]! Glad you joined us! 😊 Don't be shy, we're a friendly bunch!"
        ],
        "description": "New member welcome messages for groups"
    },
    {
        "name": "🤝 Community Event",
        "messages": [
            "📣 Community event this [DAY]! Everyone is welcome. Spread the word! 🌍",
            "Join us for our monthly community meetup! 🤝 [DATE] at [LOCATION] — See you there!",
            "Don't miss our community event! 🎊 Fun, food, and great people. [DATE] — mark it!"
        ],
        "description": "Community event announcements"
    },
    {
        "name": "🤝 Poll / Vote",
        "messages": [
            "📊 Quick poll! Reply with A or B: [OPTION_A] vs [OPTION_B] — your vote matters! 🗳️",
            "Time to vote! 🗳️ Which do you prefer? A: [OPTION_A] or B: [OPTION_B]? Reply now!",
            "Help us decide! Vote: A for [OPTION_A] or B for [OPTION_B]. Most votes wins! 🏆"
        ],
        "description": "Community poll and voting messages"
    },

    # ── 11. REAL ESTATE & SERVICES ────────────────────────────────────────────
    {
        "name": "🏠 Property Listing",
        "messages": [
            "🏠 NEW LISTING! [BEDROOMS]BR/[BATHROOMS]BA in [LOCATION] — Price: $[PRICE]. Call now! 📞",
            "Just listed! Beautiful property in [LOCATION]. [SQFT] sq ft, move-in ready! DM for details 🔑",
            "Property alert! 🏡 Your dream home just hit the market in [NEIGHBORHOOD]. Interested? 👀"
        ],
        "description": "Real estate property listing messages"
    },
    {
        "name": "🏠 Open House Invite",
        "messages": [
            "🏡 Open House this [DAY] from [TIME] to [TIME] at [ADDRESS]. Come take a look! 🔑",
            "You're invited to our Open House! 🏠 [DATE] at [TIME] — [ADDRESS]. Light refreshments served!",
            "Open House Alert! 🎉 Tour your future home on [DATE]. RSVP to confirm attendance 📅"
        ],
        "description": "Real estate open house invitations"
    },
    {
        "name": "🏠 Rent Due Reminder",
        "messages": [
            "Hi [TENANT]! This is a friendly reminder that rent of $[AMOUNT] is due on [DATE]. Thank you! 🏠",
            "Rent reminder! 📅 Your payment of $[AMOUNT] is due by [DATE]. Please ensure timely payment.",
            "Gentle reminder: rent is due [DATE]. Contact us if you have any questions 😊 Thank you!"
        ],
        "description": "Tenant rent due reminder messages"
    },

    # ── 12. RESTAURANT & FOOD ─────────────────────────────────────────────────
    {
        "name": "🍽️ Daily Special",
        "messages": [
            "🍽️ TODAY'S SPECIAL: [DISH] — only $[PRICE]! Available while supplies last. Order now! 🛵",
            "Chef's Special today: [DISH] 🧑‍🍳 Made with fresh ingredients. Limited portions — order fast!",
            "Lunch special! 🌮 [DISH] for just $[PRICE] today only. Call us or order online! 📱"
        ],
        "description": "Restaurant daily special announcements"
    },
    {
        "name": "🍽️ Reservation Confirmation",
        "messages": [
            "✅ Your reservation at [RESTAURANT] is confirmed! Date: [DATE], Time: [TIME], Party of [NUMBER]. See you soon!",
            "Reservation confirmed! 🍽️ We look forward to seeing you on [DATE] at [TIME]. See you there!",
            "Your table is reserved! 🥂 [DATE] at [TIME] for [NUMBER] guests. Let us know if plans change!"
        ],
        "description": "Restaurant reservation confirmation messages"
    },
    {
        "name": "🍽️ Menu Update",
        "messages": [
            "📋 Exciting news! We've updated our menu with amazing new dishes! Come taste the difference 😋",
            "New menu items just dropped! 🆕🍽️ Come in and try something new — you won't be disappointed!",
            "Menu refresh! 🎉 Seasonal dishes are now available. Reserve your table before spots run out! 📞"
        ],
        "description": "Restaurant menu update announcements"
    },

    # ── BONUS ─────────────────────────────────────────────────────────────────
    {
        "name": "📣 Broadcast — Urgent",
        "messages": [
            "🚨 URGENT NOTICE: Please read the following important update: [MESSAGE]",
            "⚠️ IMPORTANT: This requires your immediate attention. [ACTION_REQUIRED]",
            "🔔 ALERT: [TITLE] — [DETAILS]. Please respond ASAP."
        ],
        "description": "Urgent broadcast notification templates"
    },
    {
        "name": "📣 Broadcast — Informational",
        "messages": [
            "📢 UPDATE: [TOPIC] — [DETAILS]. Questions? Reply to this message.",
            "ℹ️ FYI: [INFORMATION]. No action required at this time.",
            "📨 ANNOUNCEMENT: [CONTENT]. Thank you for your attention!"
        ],
        "description": "Informational broadcast templates"
    },
    {
        "name": "🎯 Re-engagement Campaign",
        "messages": [
            "Hey! It's been a while 👋 We miss you! Come check out what's new — special offer inside 🎁",
            "Long time no see! 😊 We have something special just for you. Click to find out! 🔓",
            "We noticed you've been away 💙 Come back and see what you've been missing! Welcome back deal inside 🎉"
        ],
        "description": "Win-back / re-engagement campaign messages"
    },
    {
        "name": "🔔 Webinar / Live Event",
        "messages": [
            "📹 JOIN US LIVE! [EVENT_NAME] starts in [TIME]. Register now: [LINK] — don't miss it! 🎤",
            "Webinar reminder! 🖥️ [TOPIC] is happening today at [TIME]. Join us: [LINK]",
            "LIVE in [HOURS] hours! 🎬 [EVENT_NAME] — tune in: [LINK]. Bring your questions! 💬"
        ],
        "description": "Webinar and live event promotion messages"
    },
    {
        "name": "🛒 Abandoned Cart Recovery",
        "messages": [
            "Hey! You left something behind 🛒 Your cart is waiting! Complete your order before it sells out → [LINK]",
            "Don't forget your items! 🛍️ Your cart expires soon — grab them now with 10% off: [CODE]",
            "Your cart misses you! 💔 Complete your purchase today and enjoy free shipping → [LINK]"
        ],
        "description": "E-commerce abandoned cart recovery messages"
    },
    {
        "name": "👶 Baby Announcement",
        "messages": [
            "🍼 We're thrilled to announce the arrival of [BABY_NAME]! [WEIGHT], born [DATE]. Mom and baby are doing great! 💕",
            "IT'S A [BOY/GIRL]! 🎀 Welcome to the world [NAME]! Born [DATE]. Our hearts are so full! 👶❤️",
            "Our family just got bigger! 🥰 Meet [BABY_NAME], born [DATE]. Thank you for all the love and support! 👶🌸"
        ],
        "description": "Baby birth announcement messages"
    },
    {
        "name": "🛒 Feedback Survey",
        "messages": [
            "Hi! Thanks for choosing us 😊 How was your experience? Take our 1-minute survey to help us improve: [LINK] 🙏",
            "Your feedback matters! 🌟 Rate us from 1-10 on your recent purchase: [LINK]",
            "Quick question — how can we make your experience even better? Let us know here: [LINK] 💬"
        ],
        "description": "Customer feedback and satisfaction surveys"
    },
    {
        "name": "💼 Networking Request",
        "messages": [
            "Hi [NAME]! I saw your profile and loved your work in [FIELD] 🤝 Would love to connect and chat sometime!",
            "Hello! Let's connect. I'm building [PROJECT/BUSINESS] and would love to exchange ideas with you! 🚀",
            "Hey! Hope you're doing well. I'd love to grab a virtual coffee and learn more about your journey! ☕"
        ],
        "description": "Professional networking and outreach templates"
    },
    {
        "name": "🌿 Mindfulness Breathing",
        "messages": [
            "Time to breathe 🧘‍♂️ Take a deep breath in... hold for 4 seconds... and let it go. Relax your shoulders. 🌸",
            "Self-care reminder! 🍃 Step away from the screen for 2 minutes. Close your eyes and focus on your breath.",
            "Inhale peace, exhale stress 🕯️ You are doing great. Keep moving forward one step at a time."
        ],
        "description": "Mindfulness, stress relief, and breathing reminders"
    },
    {
        "name": "🛎️ Password Reset Support",
        "messages": [
            "Forgot your password? 🔒 No worries! Click this link to reset it: [LINK]. This link expires in 15 minutes.",
            "Security Alert: A password reset request was made for your account. If this was you, reset here: [LINK] 🔑",
            "Here is your temporary login code: [CODE] 🛡️ Do not share this code with anyone."
        ],
        "description": "Security and account recovery support templates"
    },
    {
        "name": "🏠 Maintenance Notice",
        "messages": [
            "📢 Scheduled Maintenance: We will be performing upgrades on [DATE] from [START_TIME] to [END_TIME]. Expect temporary downtime.",
            "⚠️ Attention Residents: Water supply will be temporarily shut off for maintenance on [DATE] from [TIME] 🚰",
            "Building Update: [FACILITY] will be closed for cleaning tomorrow between [TIME]. Thank you for your patience! 🛠️"
        ],
        "description": "Home, community, or system maintenance alerts"
    },
    {
        "name": "🎉 Happy Anniversary (Business)",
        "messages": [
            "Happy Work Anniversary to [NAME]! 🥳 Thank you for [NUMBER] years of dedication, hard work, and great vibes! 🌟",
            "Celebrating [NUMBER] years at [COMPANY]! 🎉 So proud of everything we've built together. Here's to more success! 🥂",
            "Cheers to [NUMBER] years! 🏆 Thank you for being such an invaluable part of our team! Let's celebrate! 🎂"
        ],
        "description": "Employee or business partnership anniversary wishes"
    },
    {
        "name": "📣 System Outage Update",
        "messages": [
            "🚨 Service Outage: We are currently experiencing issues with [SYSTEM]. Our team is investigating and working on a fix ASAP!",
            "⚠️ Status Update: [SYSTEM] is now partially restored. We expect full functionality to return within the hour. Thank you for your patience!",
            "✅ All Systems Operational: The issues with [SYSTEM] have been fully resolved. We apologize for any inconvenience caused. 🛠️"
        ],
        "description": "System status and downtime updates"
    },
]


class PresetManager:
    """Manages the full lifecycle of message presets."""

    def __init__(self, presets_path: str = None):
        self.presets_path = presets_path or PRESETS_PATH
        self.presets: list = []
        if not self.load_presets_from_file():
            self.presets = DEFAULT_PRESETS.copy()
            self.save_presets_to_file()

    # ── Persistence ────────────────────────────────────────────────────────────

    def load_presets_from_file(self) -> bool:
        try:
            if os.path.exists(self.presets_path):
                with open(self.presets_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list) and data:
                    self.presets = data
                    return True
        except Exception as e:
            print(f"[PresetManager] Load error: {e}")
        return False

    def save_presets_to_file(self) -> bool:
        try:
            with open(self.presets_path, "w", encoding="utf-8") as f:
                json.dump(self.presets, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[PresetManager] Save error: {e}")
            return False

    # ── CRUD ───────────────────────────────────────────────────────────────────

    def get_preset(self, index: int) -> dict | None:
        if 0 <= index < len(self.presets):
            return self.presets[index]
        return None

    def get_preset_by_name(self, name: str) -> dict | None:
        for p in self.presets:
            if p.get("name", "").lower() == name.lower():
                return p
        return None

    def get_preset_names(self) -> list[str]:
        return [p.get("name", f"Preset {i}") for i, p in enumerate(self.presets)]

    def get_messages_from_preset(self, preset_name_or_index) -> list[str]:
        if isinstance(preset_name_or_index, int):
            preset = self.get_preset(preset_name_or_index)
        else:
            preset = self.get_preset_by_name(preset_name_or_index)
        if not preset:
            return []
        if "messages" in preset:
            return preset["messages"]
        if "message" in preset:
            return [preset["message"]]
        return []

    def add_preset(self, name: str, message, description: str = "User preset") -> bool:
        if not name.strip():
            return False
        entry = {"name": name.strip(), "description": description}
        if isinstance(message, list):
            entry["messages"] = message
        else:
            entry["message"] = message
        self.presets.append(entry)
        self.save_presets_to_file()
        return True

    def update_preset(self, index: int, name: str, message,
                      description: str = "User preset") -> bool:
        if 0 <= index < len(self.presets):
            entry = {"name": name.strip(), "description": description}
            if isinstance(message, list):
                entry["messages"] = message
            else:
                entry["message"] = message
            self.presets[index] = entry
            self.save_presets_to_file()
            return True
        return False

    def delete_preset(self, index: int) -> bool:
        if 0 <= index < len(self.presets):
            del self.presets[index]
            self.save_presets_to_file()
            return True
        return False

    def reset_to_defaults(self):
        self.presets = DEFAULT_PRESETS.copy()
        self.save_presets_to_file()
        return True


if __name__ == "__main__":
    pm = PresetManager()
    print(f"Total presets loaded: {len(pm.presets)}")
    for i, p in enumerate(pm.presets):
        msgs = pm.get_messages_from_preset(i)
        print(f"  [{i+1:02d}] {p['name']}  ({len(msgs)} message{'s' if len(msgs)!=1 else ''})")