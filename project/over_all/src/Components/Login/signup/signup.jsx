import React from 'react';
import { useNavigate } from 'react-router-dom'; // Import the useNavigate hook
import './SignUp.css'; // Create a CSS file for styling

const SignUp = () => {
    const navigate = useNavigate(); // Initialize the navigate function

    // Function to handle the "Sign In" button click
    const handleSignInClick = () => {
      navigate('/signin'); // Navigate to the sign-in page
    };
  return (

    <div id = "signuppage">
    <div className="signup-container">
      <h2>Sign Up</h2>
      <form>
        <div className="container">
          <label htmlFor="email"><b>Email</b></label>
          <input type="text" placeholder="Enter Email" name="email" required />

          <label htmlFor="password"><b>Password</b></label>
          <input type="password" placeholder="Enter Password" name="password" required />

          <label htmlFor="designation"><b>Designation</b></label>
          <input type="text" placeholder="Enter Designation" name="designation" required />

          <button type="submit">Sign Up</button>
        </div>

        <div className="container">
        <button
              type="button"
              className="signin"
              onClick={handleSignInClick} // Attach the click handler
            >
              Sign In
            </button>        </div>
      </form>
    </div>
    </div>
  );
};

export default SignUp;
