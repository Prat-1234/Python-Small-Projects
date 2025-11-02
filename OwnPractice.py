def detailed_password_comparison(password1, password2):
    mismatch_count = 0
    mismatch_details = []

    min_len = min(len(password1), len(password2))

    # Compare character by character
    for i in range(min_len):
        char1 = password1[i]
        char2 = password2[i]
        if char1 != char2:
            mismatch_count += 1
            if char1.lower() == char2.lower():
                mismatch_details.append(f"❌ Case mismatch at position {i+1}: '{char1}' vs '{char2}'")
            elif char1.isdigit() and char2.isdigit():
                mismatch_details.append(f"❌ Digit mismatch at position {i+1}: '{char1}' vs '{char2}'")
            else:
                mismatch_details.append(f"❌ Character mismatch at position {i+1}: '{char1}' vs '{char2}'")

    # Count extra characters due to length mismatch
    length_diff = abs(len(password1) - len(password2))
    if length_diff > 0:
        mismatch_count += length_diff
        if mismatch_count < 3:  # only show if < 3 mismatches total
            mismatch_details.append("❌ Length mismatch.")

    # Final result
    if mismatch_count >= 3:
        return "❌ Passwords do not match", ""
    elif mismatch_count > 0:
        return "⚠️ Passwords Do Not Match", "\n".join(mismatch_details)
    else:
        return "✅ Passwords Match Perfectly 🎉", ""

# --- Main Program ---
if __name__ == "__main__":
    password1 = input("Enter 1st password: ")
    password2 = input("Enter 2nd password: ")

    result, feedback = detailed_password_comparison(password1, password2)
    print("\nResult:", result)
    if feedback:
        print("Details:\n" + feedback)
