import React, { useState } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Alert, TextInput } from 'react-native';
import { correctWord, confirmCorrection } from "../api";


export default function Profile({ navigation, route }) {

  const [inputWord, setInputWord] = useState(""); 
  const[result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCorrect = async () => {
  if (!inputWord.trim()) return;

  try {
    setLoading(true);
    const response = await correctWord(inputWord);
    setResult(response);
  } catch (err) {
    Alert.alert("Error", "Failed to connect to AI backend");
  } finally {
    setLoading(false);
  }
};

  const handleConfirm = async () => {
  if (!result) return;
    try {
        await confirmCorrection(result.original, result.corrected);
        Alert.alert("Saved", "Correction learned successfully");
    } catch {
        Alert.alert("Error", "Failed to save correction");
    }
 };


  const firstName = route?.params?.firstName || 'User';

  const handleDeleteAccount = () => {
    Alert.alert(
      "Confirm Deletion",
      "Are you sure you want to delete your account? This action cannot be undone.",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Delete",
          style: "destructive",
          onPress: () => {
            // Reset stack to SignUp only
            navigation.reset({
              index: 0,
              routes: [{ name: 'SignUp' }],
            });
          }
        }
      ]
    );
  };

  const handleLogout = () => {
    Alert.alert(
      "Confirm Log Out",
      "Are you sure you want to log out?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Log Out",
          style: "destructive",
          onPress: () => {
            // 🚀 Reset stack to Login only, no leftover Splash/Profile
            navigation.reset({
              index: 0,
              routes: [{ name: 'Splash' }],
            });
          }
        }
      ]
    );
  };

  const handleChangePassword = () => {
    Alert.alert(
      "Change Password",
      "Password change flow would open here.",
      [{ text: "OK" }]
    );
  };

  const handleBack = () => {
    if (navigation.canGoBack()) {
      navigation.goBack();
    } else {
      navigation.reset({
        index: 0,
        routes: [{ name: 'Splash', params: { firstName } }],
      });
    }
  };

  return (
    <View style={styles.container}>
      <TextInput
  style={styles.input}
  placeholder="Enter word"
  placeholderTextColor="#888"
  value={inputWord}
  onChangeText={setInputWord}
/>

<TouchableOpacity style={styles.primaryButton} onPress={handleCorrect}>
  <Text style={styles.primaryText}>
    {loading ? "Thinking..." : "Correct Word"}
  </Text>
</TouchableOpacity>

{result && (
  <>
    <Text style={styles.infoText}>
      Corrected: {result.corrected}
    </Text>

      <TouchableOpacity style={styles.secondaryButton} onPress={handleConfirm}>
        <Text style={styles.secondaryText}>Confirm Correction</Text>
      </TouchableOpacity>
  </>
)}

      <TouchableOpacity style={styles.backButton} onPress={handleBack}>
        <Text style={styles.backText}>{'<'}</Text>
      </TouchableOpacity>

      <Text style={styles.title}>Profile</Text>
      <View style={styles.avatar} />
      <Text style={styles.name}>{firstName}</Text>

      <View style={styles.infoBox}>
        <Text style={styles.infoText}>Phone: (123) 456-7890</Text>
        <Text style={styles.infoText}>Extension added: Nov 2025</Text>
        <Text style={styles.infoText}>Role: Premium Member</Text>

        <TouchableOpacity style={styles.primaryButton} onPress={handleChangePassword}>
          <Text style={styles.primaryText}>Change Password</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.secondaryButton} onPress={handleLogout}>
          <Text style={styles.secondaryText}>Log Out</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.destructiveButton} onPress={handleDeleteAccount}>
          <Text style={styles.destructiveText}>Delete Account</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000000', alignItems: 'center', paddingTop: 100 },
  backButton: { position: 'absolute', top: 50, left: 20, padding: 10 },
  backText: { fontSize: 28, color: '#00ffff', fontWeight: '700' },
  title: { fontSize: 28, fontWeight: '700', color: '#f5f5f5', marginBottom: 20 },
  avatar: { width: 120, height: 120, borderRadius: 60, backgroundColor: '#1e1e1e', borderWidth: 2, borderColor: '#00ffff', marginBottom: 15 },
  name: { fontSize: 24, fontWeight: '600', color: '#00ffff', marginBottom: 20 },
  infoBox: { width: '85%', padding: 20, borderRadius: 12, backgroundColor: '#1e1e1e' },
  infoText: { fontSize: 18, color: '#f5f5f5', marginVertical: 8 },

  primaryButton: { marginTop: 16, alignItems: 'center', paddingVertical: 10, borderRadius: 8, backgroundColor: '#00ffff' },
  primaryText: { fontSize: 18, fontWeight: '700', color: '#000' },

  secondaryButton: { marginTop: 12, alignItems: 'center', paddingVertical: 10, borderRadius: 8, backgroundColor: '#333' },
  secondaryText: { fontSize: 18, fontWeight: '700', color: '#f5f5f5' },

  destructiveButton: { marginTop: 12, alignItems: 'center', paddingVertical: 10, borderRadius: 8, backgroundColor: '#ff4d4d' },
  destructiveText: { fontSize: 18, fontWeight: '700', color: '#000' },
  input: {
  marginTop: 12,
  padding: 10,
  borderRadius: 8,
  backgroundColor: "#000",
  color: "#f5f5f5",
  borderWidth: 1,
  borderColor: "#00ffff",
}

});