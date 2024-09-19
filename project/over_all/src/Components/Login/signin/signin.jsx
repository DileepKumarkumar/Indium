import React, { useState } from "react";
import './signin.css'; // Import the CSS file for other styles
import backgroundImage from './icon.jpg'; // Adjust the path to your image
import backgroundImage1 from './Game-Automation-–-When-we-talk-about-game-testing.png';
import { useNavigate } from "react-router-dom";

const Signin = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [isResettingPassword, setIsResettingPassword] = useState(false);
  const navigate = useNavigate();

  // Handle sign-up navigation
  const handleSignupClick = () => {
    navigate("/signup");
  };

  // Handle forgot password link click
  const handleForgotPasswordClick = () => {
    setIsResettingPassword(true);
  };

  // Handle password reset form submission
  const handleResetPassword = (e) => {
    e.preventDefault();
    // Add logic for password reset here
    setIsResettingPassword(false);
  };

  // Function to handle login form submission
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://127.0.0.1:8000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        alert(data.message);

        // Call the onLogin handler passed as a prop from App.jsx to update authentication state
        onLogin();

        // Navigate to home or dashboard page after successful login
        navigate("/dashboard");
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Invalid credentials. Please try again.");
      }
    } catch (error) {
      console.error("Error during login:", error);
      setError("Something went wrong. Please try again.");
    }
  };

  return (
    <div
      id="signinpage"
      style={{
        backgroundImage: `url(${backgroundImage1}), url(${backgroundImage})`,
        backgroundSize: '50% 100%, 50% 100%',
        backgroundPosition: 'left, right',
        backgroundRepeat: 'no-repeat, no-repeat',
        width: '100vw',
        height: '100vh',
      }}
    >
      <div id="signin">
        {isResettingPassword ? (
          <div>
            <h2>Reset Password</h2>
            <form onSubmit={handleResetPassword}>
              <div className="container">
                <label htmlFor="new-password"><b>New Password</b></label>
                <input
                  type="password"
                  placeholder="Enter New Password"
                  name="new-password"
                  required
                />
                <label htmlFor="confirm-password"><b>Confirm Password</b></label>
                <input
                  type="password"
                  placeholder="Re-enter New Password"
                  name="confirm-password"
                  required
                />
                <button type="submit">Reset Password</button>
              </div>
              <div className="container">
                <button
                  type="button"
                  className="cancelbtn"
                  onClick={() => setIsResettingPassword(false)}
                >
                  Back to Sign In
                </button>
              </div>
            </form>
          </div>
        ) : (
          <div>
            <h2>Login Form</h2>
            <form onSubmit={handleLogin}>
              <div className="container">
                <label htmlFor="uname"><b>Username</b></label>
                <input
                  type="text"
                  placeholder="Enter Username"
                  name="uname"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
                <label htmlFor="psw"><b>Password</b></label>
                <input
                  type="password"
                  placeholder="Enter Password"
                  name="psw"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button type="submit">Login</button>
                {error && <p style={{ color: 'red' }}>{error}</p>}
                <label id="Rememberme">
                  <input type="checkbox" name="remember" defaultChecked /> Remember me
                </label>
                <span className="psw">
                  <a href="#" onClick={handleForgotPasswordClick}>Forgot password?</a>
                </span>
              </div>
              <div className="container" style={{ backgroundColor: "#f1f1f1" }}>
                <button type="button" className="Signup" onClick={handleSignupClick}>
                  Sign Up
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default Signin;
