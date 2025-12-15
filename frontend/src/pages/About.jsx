import React, { useState } from 'react';
import './About.css';

const About = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        subject: 'support',
        message: ''
    });

    const [status, setStatus] = useState({ type: '', msg: '' });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        setStatus({ type: '', msg: '' });

        // Simulate API call
        setTimeout(() => {
            setIsSubmitting(false);
            setStatus({ type: 'success', msg: 'Message sent successfully! We will get back to you soon.' });
            setFormData({ ...formData, message: '' });
        }, 1500);
    };

    const team = [
        {
            name: "Roshan Varghese",
            id: "2448046",
            role: "Multiagent System & Backend Lead",
            avatar: "👨‍💻",
            desc: "5MDS, Christ (Deemed to be University). Architecting the Hybrid Neuro-Symbolic Agent System and backend integration.",
            links: {
                email: "mailto:roshan.varghese@msds.christuniversity.in",
                linkedin: "https://www.linkedin.com/in/roshan-varghese-022986217",
                github: "https://github.com/RoshanVarghese",
                portfolio: "https://app.roshanvarghese.world"
            }
        },
        {
            name: "Varun Alfred Desouza",
            id: "2448059",
            role: "Frontend & RAG Pipeline Developer",
            avatar: "👨‍💻",
            desc: "5MDS, Christ (Deemed to be University). Specializing in Agentic RAG implementation, UI/UX, and Documentation.",
            links: {
                email: "mailto:varunalfred.dsouza@msds.christuniversity.in",
                linkedin: "https://www.linkedin.com/in/varunsouz/",
                github: "https://github.com/varunalfred",
                portfolio: null
            }
        }
    ];

    const techStack = [
        { name: "React 18", icon: "⚛️" },
        { name: "Tailwind CSS", icon: "🎨" },
        { name: "Vite", icon: "⚡" },
        { name: "FastAPI", icon: "🚀" },
        { name: "Google Gemini", icon: "🧠" },
        { name: "DSPy", icon: "🎯" },
        { name: "LangChain", icon: "🔗" },
        { name: "PostgreSQL", icon: "🐘" },
        { name: "pgvector", icon: "🔍" },
        { name: "yfinance", icon: "📈" }
    ];

    return (
        <div className="about-container">
            {/* Hero Section */}
            <section className="about-hero">
                <div className="hero-content">
                    <h1>About <span className="highlight">FinMentor AI</span></h1>
                    <p className="system-brief">
                        FinMentor AI is a novel multi-agent financial advisory platform designed to democratize institutional-grade investment guidance.
                        Unlike static chatbots, it utilizes a <strong>Hybrid Neuro-Symbolic Architecture</strong>, combining the reasoning capabilities of
                        Large Language Models (LLMs) via DSPy with the deterministic execution of LangChain tools to provide precise, verifiable,
                        and personalized financial advice.
                    </p>
                </div>
            </section>

            {/* System Overview */}
            <section className="about-section system-overview">
                <h2>The System</h2>
                <div className="features-grid-about">
                    <div className="feature-item">
                        <span className="feature-icon">🤖</span>
                        <h3>Hybrid Neuro-Symbolic AI</h3>
                        <p>Combines the reasoning of LLMs (DSPy) with deterministic execution (LangChain) for verifiable advice.</p>
                    </div>
                    <div className="feature-item">
                        <span className="feature-icon">🧬</span>
                        <h3>Agentic RAG</h3>
                        <p>Intelligently routes queries to Real-time Market Data (Yahoo Finance) or Educational Content (PGVector).</p>
                    </div>
                    <div className="feature-item">
                        <span className="feature-icon">🔒</span>
                        <h3>Secure & Private</h3>
                        <p>Bridging the "GenAI Gap" with enterprise-grade security and personalized risk profiling.</p>
                    </div>
                </div>
            </section>

            {/* Developers / Team */}
            <section className="about-section team-section">
                <h2>The Team</h2>
                <p className="section-subtitle">Christ (Deemed to be University) - 5MDS</p>
                <div className="team-grid">
                    {team.map((member, index) => (
                        <div key={index} className="team-card glass-card">
                            <div className="member-avatar">{member.avatar}</div>
                            <h3>{member.name}</h3>
                            <div className="member-id" style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '0.5rem' }}>ID: {member.id}</div>
                            <div className="member-role">{member.role}</div>
                            <p>{member.desc}</p>

                            {/* Social Links */}
                            <div className="member-links">
                                <a href={member.links.email} title="Email" className="social-link">📧</a>
                                <a href={member.links.linkedin} target="_blank" rel="noopener noreferrer" title="LinkedIn" className="social-link">🔗</a>
                                <a href={member.links.github} target="_blank" rel="noopener noreferrer" title="GitHub" className="social-link">💻</a>
                                {member.links.portfolio && (
                                    <a href={member.links.portfolio} target="_blank" rel="noopener noreferrer" title="Portfolio" className="social-link">🌐</a>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* Tech Stack */}
            <section className="about-section tech-section">
                <h2>Technology Stack</h2>
                <div className="tech-badge-container">
                    {techStack.map((tech, index) => (
                        <div key={index} className="tech-badge">
                            <span className="tech-icon">{tech.icon}</span>
                            <span className="tech-name">{tech.name}</span>
                        </div>
                    ))}
                </div>
            </section>

            {/* Contact Form */}
            <section className="about-section contact-section" id="contact">
                <div className="contact-wrapper glass-card">
                    <div className="contact-info">
                        <h2>Get in Touch</h2>
                        <p>Project Feedback & Inquiries</p>

                        <div className="contact-method">
                            <div className="icon">📧</div>
                            <div>
                                <label>Support Emails</label>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                                    <a href="mailto:roshan.varghese@msds.christuniversity.in" style={{ fontSize: '0.9rem' }}>roshan.varghese@msds.christuniversity.in</a>
                                    <a href="mailto:varunalfred.dsouza@msds.christuniversity.in" style={{ fontSize: '0.9rem' }}>varunalfred.dsouza@msds.christuniversity.in</a>
                                </div>
                            </div>
                        </div>

                        <div className="contact-method">
                            <div className="icon">🎓</div>
                            <div>
                                <label>Institution</label>
                                <span style={{ color: '#e2e8f0' }}>Christ (Deemed to be University)</span>
                            </div>
                        </div>
                    </div>

                    <form className="contact-form" onSubmit={handleSubmit}>
                        {status.msg && (
                            <div className={`form-alert ${status.type}`}>
                                {status.msg}
                            </div>
                        )}

                        <div className="form-group">
                            <label>Name</label>
                            <input
                                type="text"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                required
                                placeholder="Your Name"
                            />
                        </div>

                        <div className="form-group">
                            <label>Email</label>
                            <input
                                type="email"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                required
                                placeholder="your@email.com"
                            />
                        </div>

                        <div className="form-group">
                            <label>Subject</label>
                            <select
                                value={formData.subject}
                                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                            >
                                <option value="support">Technical Support</option>
                                <option value="feedback">Project Feedback</option>
                                <option value="other">Other</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label>Message</label>
                            <textarea
                                value={formData.message}
                                onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                                required
                                rows="5"
                                placeholder="Write your message here..."
                            ></textarea>
                        </div>

                        <button type="submit" className="btn-send" disabled={isSubmitting}>
                            {isSubmitting ? 'Sending...' : 'Send Message'}
                        </button>
                    </form>
                </div>
            </section>
        </div>
    );
};

export default About;
