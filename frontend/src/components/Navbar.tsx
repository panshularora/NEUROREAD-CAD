import React from 'react';

type NavKey = 'home' | 'simplifier' | 'dashboard' | 'history' | 'settings' | 'about';

interface NavbarProps {
  active?: NavKey;
  onChange?: (key: NavKey) => void;
}

const Navbar: React.FC<NavbarProps> = ({ active = 'simplifier', onChange }) => {
  const makeHandler = (key: NavKey) => () => {
    onChange?.(key);
  };

  return (
    <nav className="navbar-root" aria-label="Primary navigation">
      <div className="navbar-track">
        <button
          type="button"
          className={`navbar-pill ${active === 'home' ? 'is-active' : ''}`}
          onClick={makeHandler('home')}
        >
          <span className="navbar-icon">
            {/* home icon */}
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M4 11 12 4l8 7v7.25c0 .69-.56 1.25-1.25 1.25H5.25A1.25 1.25 0 0 1 4 18.25V11Z"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </span>
          <span className="navbar-label">Home</span>
        </button>

        <button
          type="button"
          className={`navbar-pill ${active === 'simplifier' ? 'is-active' : ''}`}
          onClick={makeHandler('simplifier')}
        >
          <span className="navbar-icon">
            {/* cube / processing icon */}
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M5.25 8.5 12 4.75l6.75 3.75V15.5L12 19.25 5.25 15.5V8.5Z"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M12 12.5v6.75"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.4"
                strokeLinecap="round"
              />
            </svg>
          </span>
          <span className="navbar-label">Simplifier</span>
        </button>

        <button
          type="button"
          className={`navbar-pill ${active === 'dashboard' ? 'is-active' : ''}`}
          onClick={makeHandler('dashboard')}
        >
          <span className="navbar-icon">
            {/* monitoring bars icon */}
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M6 18V9.5M12 18V6M18 18v-4.5"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
              />
            </svg>
          </span>
          <span className="navbar-label">Dashboard</span>
        </button>

        <button
          type="button"
          className={`navbar-pill ${active === 'history' ? 'is-active' : ''}`}
          onClick={makeHandler('history')}
        >
          <span className="navbar-icon">
            {/* clock / history icon */}
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M4.5 12A7.5 7.5 0 1 1 12 19.5"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
              />
              <path
                d="M12 7v5l3 2"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M4.5 8.5V4.5h4"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </span>
          <span className="navbar-label">History</span>
        </button>

        <button
          type="button"
          className={`navbar-pill ${active === 'settings' ? 'is-active' : ''}`}
          onClick={makeHandler('settings')}
        >
          <span className="navbar-icon">
            {/* settings / cog icon */}
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M11.25 3.5 10.5 5.5l-1.7.6-1.7-1.2L4 7.5l1.2 1.7-.6 1.7-2 .75v2.5l2 .75.6 1.7L4 18.5l3.1 2.6 1.7-1.2 1.7.6.75 2h2.5l.75-2 1.7-.6 1.7 1.2 3.1-2.6-1.2-1.7.6-1.7 2-.75v-2.5l-2-.75-.6-1.7 1.2-1.7-3.1-2.6-1.7 1.2-1.7-.6-.75-2h-2.5Z"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.1"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <circle
                cx="12"
                cy="12"
                r="3"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
              />
            </svg>
          </span>
          <span className="navbar-label">Settings</span>
        </button>

        <button
          type="button"
          className={`navbar-pill ${active === 'about' ? 'is-active' : ''}`}
          onClick={makeHandler('about')}
        >
          <span className="navbar-icon">
            {/* chat / help icon */}
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M6 18.5 4.5 21l2.5-.8A10 10 0 1 0 4 12"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M8.5 10.75h7M8.5 13.75h4.5"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
              />
            </svg>
          </span>
          <span className="navbar-label">About / Help</span>
        </button>

        {/* search icon-only pill, matching reference */}
        <button
          type="button"
          className="navbar-pill navbar-pill-icon-only"
          aria-label="Search"
        >
          <span className="navbar-icon">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <circle
                cx="11"
                cy="11"
                r="5"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              />
              <path
                d="m15 15 4 4"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
              />
            </svg>
          </span>
        </button>
      </div>
    </nav>
  );
};

export default Navbar;

