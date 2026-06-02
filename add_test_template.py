#!/usr/bin/env python3
"""Script to add a comprehensive test template with lengthy content."""

import sys
sys.path.insert(0, '/home/karthik/DEV/Our Web Application/Dynamic_Websites/admin/backend')

from services.db import get_db
from datetime import datetime, timezone
from bson import ObjectId
import copy

BLANK_CONFIG = {
    "siteId": "",
    "logo": "",
    "theme": {
        "primaryColor": "#4f46e5", "secondaryColor": "#06b6d4",
        "accentColor": "#f59e0b", "bgColor": "#ffffff",
        "textColor": "#1f2937", "mutedColor": "#6b7280",
        "darkBg": "#0f172a", "fontBody": "'Inter', sans-serif",
        "fontHeading": "'Poppins', sans-serif"
    },
    "header": {"template": 1, "phone": "", "email": "",
        "navLinks": [
            {"label": "Home", "page": "home"},
            {"label": "Services", "page": "services"},
            {"label": "Achievements", "page": "achievements"},
            {"label": "About Us", "page": "about"},
            {"label": "Contact", "page": "contact"},
            {"label": "Feedback", "page": "feedback"}
        ]
    },
    "footer": {"template": 1, "description": "", "address": "", "phone": "", "email": "", "copyrightYear": 2024},
    "socialLinks": {"facebook": "", "twitter": "", "instagram": "", "linkedin": ""},
    "pages": {
        "home": {"template": 1, "titleTemplate": 1, "title": "", "subtitle": "", "heroImage": "", "features": [], "stats": [], "testimonials": []},
        "services": {"template": 1, "titleTemplate": 1, "title": "Our Services", "subtitle": "", "heroImage": "", "items": []},
        "achievements": {"template": 1, "titleTemplate": 1, "title": "Achievements", "subtitle": "", "heroImage": "", "awards": [], "milestones": [], "stats": []},
        "about": {"template": 1, "titleTemplate": 1, "title": "About Us", "subtitle": "", "heroImage": "", "story": "", "mission": "", "vision": "", "values": [], "team": []},
        "contact": {"template": 1, "titleTemplate": 1, "title": "Contact Us", "subtitle": "", "heroImage": "", "address": "", "phone": "", "email": "", "officeHours": "", "offices": []},
        "feedback": {"template": 1, "titleTemplate": 1, "title": "Feedback", "subtitle": "", "heroImage": "", "categories": ["General", "Quality", "Support", "Other"]}
    }
}

db = get_db()

# Check if template already exists
existing = db.templates.find_one({"name": "Content Testing Platform"})
if existing:
    print("✓ Template already exists. Skipping...")
    sys.exit(0)

config = copy.deepcopy(BLANK_CONFIG)
config["siteId"] = "content_testing_platform"

template_doc = {
    "name": "Content Testing Platform",
    "description": "Comprehensive template with lengthy content in all fields for UI/UX testing and validation across different screen sizes and content lengths",
    "enabled": True,
    "config": {
        **config,
        "logo": "https://via.placeholder.com/200x60?text=CTP",
        "header": {
            **config["header"],
            "phone": "+1 (555) 987-6543",
            "email": "hello@contentplatform.io"
        },
        "footer": {
            "template": 1,
            "description": "Content Testing Platform - A comprehensive solution for testing UI layouts with real-world content lengths. This platform helps designers and developers validate their responsive designs with actual lengthy content across all fields including titles, descriptions, feature names, and more.",
            "address": "123 Innovation Street, Suite 500, Technology Park, San Francisco, CA 94105, United States",
            "phone": "+1 (555) 987-6543",
            "email": "support@contentplatform.io",
            "copyrightYear": 2024
        },
        "socialLinks": {
            "facebook": "https://facebook.com/contentplatform",
            "twitter": "https://twitter.com/contentplatform",
            "instagram": "https://instagram.com/contentplatform",
            "linkedin": "https://linkedin.com/company/contentplatform"
        },
        "pages": {
            "home": {
                "template": 3,
                "titleTemplate": 2,
                "title": "Welcome to Content Testing Platform - Comprehensive UI Testing Solution for Modern Web Applications",
                "subtitle": "Validate your responsive designs with real-world content lengths. This platform provides lengthy text samples in all fields to help you identify layout issues before they reach production.",
                "heroImage": "https://via.placeholder.com/1200x500?text=Hero+Image",
                "features": [
                    {
                        "icon": "📝",
                        "title": "Comprehensive Content Testing Framework",
                        "desc": "Our platform allows you to test your UI components with real-world content lengths. Every field contains lengthy text to help identify potential layout breaks, text overflow issues, and responsive design problems across different screen sizes and device types."
                    },
                    {
                        "icon": "📊",
                        "title": "Advanced Analytics and Performance Monitoring",
                        "desc": "Track how your layouts perform with different content lengths using our built-in analytics dashboard. Monitor performance metrics, identify bottlenecks, and get actionable insights to improve your application's user experience and overall performance."
                    },
                    {
                        "icon": "🎨",
                        "title": "Design System Integration and Customization",
                        "desc": "Seamlessly integrate with popular design systems and component libraries. Customize colors, typography, spacing, and other design tokens to match your brand guidelines while testing with varied content lengths and formats."
                    },
                    {
                        "icon": "🔧",
                        "title": "Developer-Friendly Tools and Documentation",
                        "desc": "Access comprehensive documentation, API references, and code examples to get started quickly. Our developer-friendly tools include component previews, interactive playgrounds, and detailed troubleshooting guides for common issues."
                    },
                    {
                        "icon": "🚀",
                        "title": "Performance Optimization Utilities",
                        "desc": "Identify and resolve performance bottlenecks with our optimization toolkit. Get recommendations for code splitting, lazy loading, image optimization, and other performance-enhancing techniques to ensure your application loads quickly."
                    },
                    {
                        "icon": "🔒",
                        "title": "Security and Compliance Management",
                        "desc": "Built with security best practices and compliance requirements in mind. Our platform ensures your data is protected with encryption, follows GDPR and other regulations, and provides comprehensive audit logging for compliance verification."
                    }
                ],
                "stats": [
                    {"value": "10,000+", "label": "Active Users Testing Their Designs"},
                    {"value": "500+", "label": "Component Variations Tested"},
                    {"value": "99.9%", "label": "Platform Uptime Guarantee"}
                ]
            },
            "services": {
                "template": 3,
                "titleTemplate": 3,
                "title": "Professional Services - Comprehensive Support for Your Testing Needs",
                "subtitle": "Expert guidance and support to help you get the most out of our content testing platform with detailed implementation strategies",
                "heroImage": "https://via.placeholder.com/1200x500?text=Services",
                "items": [
                    {
                        "icon": "👥",
                        "title": "Design Consultation and Strategy",
                        "image": "https://via.placeholder.com/300x200?text=Consultation",
                        "desc": "Work with our design experts to develop a comprehensive testing strategy. We analyze your current design system, identify areas for improvement, and provide actionable recommendations to enhance your user experience and component accessibility across all screen sizes and content scenarios."
                    },
                    {
                        "icon": "📚",
                        "title": "Training and Workshop Programs",
                        "image": "https://via.placeholder.com/300x200?text=Training",
                        "desc": "Participate in our comprehensive training programs designed for designers, developers, and product managers. Learn best practices for responsive design, accessibility, performance optimization, and how to effectively use our content testing platform to catch issues early in the development cycle."
                    },
                    {
                        "icon": "🔍",
                        "title": "Quality Assurance and Testing Services",
                        "image": "https://via.placeholder.com/300x200?text=QA+Services",
                        "desc": "Our QA team performs thorough testing of your designs across multiple devices, browsers, and content scenarios. We create detailed reports highlighting issues, suggest fixes, and provide recommendations for improving overall design quality and user experience consistency."
                    },
                    {
                        "icon": "🛠️",
                        "title": "Custom Integration and Development",
                        "image": "https://via.placeholder.com/300x200?text=Integration",
                        "desc": "Need custom features or integrations? Our development team can build tailored solutions that integrate seamlessly with your existing workflow. From API implementations to custom components, we handle all aspects of technical integration and customization."
                    }
                ]
            },
            "achievements": {
                "template": 3,
                "titleTemplate": 4,
                "title": "Our Achievements and Milestones - Building Excellence in Design Testing",
                "subtitle": "Celebrating our journey of innovation and helping thousands of teams build better user experiences through comprehensive content testing and validation strategies.",
                "heroImage": "https://via.placeholder.com/1200x500?text=Achievements",
                "awards": [
                    {
                        "year": 2024,
                        "title": "Best Design Testing Tool",
                        "issuer": "Tech Innovation Awards",
                        "description": "Recognized for our innovative approach to content testing and design validation. Our platform has set new standards in the industry for identifying and preventing layout issues with real-world content scenarios."
                    },
                    {
                        "year": 2023,
                        "title": "Customer Choice Award",
                        "issuer": "Design Tools Review",
                        "description": "Voted by thousands of designers and developers as their preferred platform for testing UI layouts with varied content lengths. Our ease of use and comprehensive feature set earned this prestigious recognition."
                    }
                ],
                "milestones": [
                    {
                        "date": "2024",
                        "title": "Reached 10,000+ Active Users",
                        "description": "Our platform now serves over 10,000 active users worldwide, helping them create better, more robust designs that work with any content length."
                    },
                    {
                        "date": "2023",
                        "title": "Launched Advanced Analytics",
                        "description": "Released our comprehensive analytics dashboard, allowing users to track testing metrics, identify patterns, and get actionable insights for design improvements."
                    },
                    {
                        "date": "2022",
                        "title": "Public Launch",
                        "description": "Officially launched our content testing platform to the public after months of beta testing with leading design and development teams."
                    }
                ],
                "stats": [
                    {"value": "10,000+", "label": "Active Users"},
                    {"value": "500+", "label": "Component Templates"},
                    {"value": "150+", "label": "Countries Represented"}
                ]
            },
            "about": {
                "template": 3,
                "titleTemplate": 5,
                "title": "About Content Testing Platform - Our Mission and Vision",
                "subtitle": "Learn about our journey, values, and commitment to helping designers and developers create exceptional user experiences through rigorous content testing and validation.",
                "heroImage": "https://via.placeholder.com/1200x500?text=About+Us",
                "story": "Content Testing Platform was founded by a team of passionate designers and developers who recognized a critical gap in the market. We realized that many layout issues and responsive design problems only became apparent when real, lengthy content was introduced into designs. Traditional design tools often focused on static layouts without accounting for variable content lengths. We set out to change that by creating a comprehensive platform specifically designed for testing UI components with real-world content scenarios. Today, we're proud to serve thousands of teams across the globe who trust our platform to catch design issues before they reach production.",
                "mission": "Our mission is to empower designers and developers to create robust, accessible, and beautiful user interfaces that work seamlessly with any content length. We believe that great design is not just about aesthetics, but about functionality and how the interface adapts to real-world data. We're committed to providing tools, resources, and support to help our community build better products that deliver exceptional user experiences.",
                "vision": "We envision a future where design testing is seamless, collaborative, and accessible to everyone. We're building the industry's most comprehensive content testing platform that combines cutting-edge technology with intuitive design. Our vision is to become the go-to solution for teams of all sizes who want to ensure their designs are bulletproof and ready for production, regardless of content variation or user scenario.",
                "values": [
                    {"title": "Excellence", "description": "We strive for excellence in everything we do, from our product features to our customer support and documentation."},
                    {"title": "Innovation", "description": "We continuously innovate and improve our platform based on user feedback and emerging industry best practices."},
                    {"title": "Accessibility", "description": "We believe quality design tools should be accessible to everyone, regardless of technical expertise or budget constraints."},
                    {"title": "Community", "description": "We foster a vibrant community where users can share knowledge, help each other, and grow together."}
                ]
            },
            "contact": {
                "template": 3,
                "titleTemplate": 6,
                "title": "Get in Touch - Contact Content Testing Platform",
                "subtitle": "Have questions about our platform? Need enterprise support? We're here to help! Reach out through any of the channels below and our team will get back to you promptly.",
                "heroImage": "https://via.placeholder.com/1200x500?text=Contact+Us",
                "address": "123 Innovation Street, Suite 500, Technology Park, San Francisco, CA 94105, United States",
                "phone": "+1 (555) 987-6543",
                "email": "support@contentplatform.io",
                "officeHours": "Monday - Friday: 9:00 AM - 6:00 PM PST | Saturday & Sunday: Closed"
            },
            "feedback": {
                "template": 3,
                "titleTemplate": 7,
                "title": "Share Your Feedback - Help Us Improve",
                "subtitle": "We value your input and feedback! Please share your thoughts, suggestions, and feature requests to help us build a better platform for everyone.",
                "heroImage": "https://via.placeholder.com/1200x500?text=Feedback",
                "categories": [
                    "Feature Request",
                    "Bug Report",
                    "Performance Feedback",
                    "UI/UX Suggestion",
                    "Documentation",
                    "General Feedback",
                    "Other"
                ]
            }
        }
    },
    "created_at": datetime.now(timezone.utc),
    "updated_at": datetime.now(timezone.utc),
}

result = db.templates.insert_one(template_doc)
print(f"✅ Template 'Content Testing Platform' created successfully with ID: {result.inserted_id}")
