/** @type {import('tailwindcss').Config} */
module.exports = {
	darkMode: ['class'],
	content: [
		'./pages/**/*.{ts,tsx}',
		'./components/**/*.{ts,tsx}',
		'./app/**/*.{ts,tsx}',
		'./src/**/*.{ts,tsx}',
	],
	theme: {
		container: {
			center: true,
			padding: {
				DEFAULT: '1rem',
				sm: '2rem',
				lg: '3rem',
			},
			screens: {
				sm: '640px',
				md: '768px',
				lg: '1024px',
				xl: '1280px',
				'2xl': '1440px',
			},
		},
		extend: {
			colors: {
				// Background colors (OLED optimized) - Enhanced hierarchy
				'bg-pure-black': '#000000',
				'bg-near-black': '#0A0E27',
				'bg-surface-dark': '#141824',
				'bg-surface-hover': '#1E2433',
				'bg-surface-modal': '#282E3F',
				
				// Text colors (high contrast) - WCAG AAA
				'text-primary': '#F8FAFC',
				'text-secondary': '#CBD5E1',
				'text-tertiary': '#94A3B8',
				'text-quaternary': '#64748B',
				'text-inverse': '#0A0A0A',
				
				// Accent colors - Enhanced semantic system
				'accent-primary': '#3B82F6',
				'accent-success': '#10B981',
				'accent-success-bright': '#34D399',
				'accent-danger': '#EF4444',
				'accent-danger-dark': '#DC2626',
				'accent-warning': '#F59E0B',
				'accent-info': '#06B6D4',
				'accent-purple': '#8B5CF6',
				
				// Performance indicators
				'perf-strong-positive': '#10B981',
				'perf-positive': '#34D399',
				'perf-neutral': '#6B7280',
				'perf-negative': '#F87171',
				'perf-strong-negative': '#EF4444',
				
				// Data quality indicators
				'quality-realtime': '#10B981',
				'quality-delayed': '#F59E0B',
				'quality-estimated': '#8B5CF6',
				
				// Chart colors
				'chart-gain': '#10B981',
				'chart-loss': '#EF4444',
			},
			fontFamily: {
				display: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
				body: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
				mono: ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
			},
			fontSize: {
				'hero': '48px',
				'h1': '36px',
				'h2': '24px',
				'h3': '20px',
				'body-lg': '18px',
				'body': '16px',
				'small': '14px',
				'price': '32px',
				'metric': '20px',
			},
			spacing: {
				'xs': '4px',
				'sm': '8px',
				'md': '16px',
				'lg': '24px',
				'xl': '32px',
				'2xl': '48px',
				'3xl': '64px',
				'4xl': '96px',
			},
			borderRadius: {
				'sm': '8px',
				'md': '12px',
				'lg': '16px',
				'full': '9999px',
			},
			boxShadow: {
				'card': '0 0 0 1px rgba(255, 255, 255, 0.06), 0 4px 12px rgba(0, 0, 0, 0.5)',
				'card-hover': '0 0 0 1px rgba(255, 255, 255, 0.12), 0 8px 24px rgba(0, 0, 0, 0.6)',
				'modal': '0 0 0 1px rgba(255, 255, 255, 0.1), 0 12px 48px rgba(0, 0, 0, 0.8)',
				'glow-primary': '0 0 20px rgba(59, 130, 246, 0.5), 0 0 40px rgba(59, 130, 246, 0.3)',
				'glow-success': '0 0 16px rgba(16, 185, 129, 0.4)',
				'glow-danger': '0 0 16px rgba(239, 68, 68, 0.4)',
			},
			keyframes: {
				'ticker-scroll': {
					'0%': { transform: 'translateX(0%)' },
					'100%': { transform: 'translateX(-50%)' },
				},
				'flash-success': {
					'0%, 100%': { boxShadow: 'none' },
					'50%': { boxShadow: '0 0 16px rgba(16, 185, 129, 0.6)' },
				},
				'flash-danger': {
					'0%, 100%': { boxShadow: 'none' },
					'50%': { boxShadow: '0 0 16px rgba(239, 68, 68, 0.6)' },
				},
				'shimmer': {
					'0%': { backgroundPosition: '-1000px 0' },
					'100%': { backgroundPosition: '1000px 0' },
				},
				'pulse-success': {
					'0%, 100%': { 
						boxShadow: '0 0 0 0 rgba(16, 185, 129, 0.4)',
						backgroundColor: 'rgba(16, 185, 129, 0.1)'
					},
					'50%': { 
						boxShadow: '0 0 12px 4px rgba(16, 185, 129, 0.2)',
						backgroundColor: 'rgba(16, 185, 129, 0.15)'
					},
				},
				'pulse-danger': {
					'0%, 100%': { 
						boxShadow: '0 0 0 0 rgba(239, 68, 68, 0.4)',
						backgroundColor: 'rgba(239, 68, 68, 0.1)'
					},
					'50%': { 
						boxShadow: '0 0 12px 4px rgba(239, 68, 68, 0.2)',
						backgroundColor: 'rgba(239, 68, 68, 0.15)'
					},
				},
				'slide-in-up': {
					'0%': { transform: 'translateY(20px)', opacity: '0' },
					'100%': { transform: 'translateY(0)', opacity: '1' },
				},
				'scale-in': {
					'0%': { transform: 'scale(0.95)', opacity: '0' },
					'100%': { transform: 'scale(1)', opacity: '1' },
				},
				'fade-in': {
					'0%': { opacity: '0' },
					'100%': { opacity: '1' },
				},
				'slide-underline': {
					'0%': { width: '0%' },
					'100%': { width: '100%' },
				},
				'progress-bar': {
					'0%': { width: '100%' },
					'100%': { width: '0%' },
				},
			},
			animation: {
				'ticker-scroll': 'ticker-scroll 30s linear infinite',
				'flash-success': 'flash-success 250ms ease-out',
				'flash-danger': 'flash-danger 250ms ease-out',
				'shimmer': 'shimmer 1.5s infinite',
				'pulse-success': 'pulse-success 600ms ease-out',
				'pulse-danger': 'pulse-danger 600ms ease-out',
				'slide-in-up': 'slide-in-up 300ms ease-out',
				'scale-in': 'scale-in 200ms ease-out',
				'fade-in': 'fade-in 400ms ease-out',
				'slide-underline': 'slide-underline 250ms ease-out',
				'progress-bar': 'progress-bar 30s linear',
			},
			transitionDuration: {
				'instant': '100ms',
				'fast': '200ms',
				'normal': '300ms',
				'slow': '400ms',
				'slower': '600ms',
			},
			transitionTimingFunction: {
				'smooth': 'cubic-bezier(0.4, 0.0, 0.2, 1)',
				'decelerate': 'cubic-bezier(0.0, 0.0, 0.2, 1)',
				'accelerate': 'cubic-bezier(0.4, 0.0, 1, 1)',
			},
		},
	},
	plugins: [require('tailwindcss-animate')],
}
