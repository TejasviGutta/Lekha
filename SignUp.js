import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity } from 'react-native';

export default function SignUp({ navigation }) {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');

  const handleSignUp = () => {
    navigation.replace('Splash', { firstName: name });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Sign Up</Text>

      <TextInput style={styles.input} placeholder="Name" placeholderTextColor="#888" value={name} onChangeText={setName} />
      <TextInput style={styles.input} placeholder="Phone Number" placeholderTextColor="#888" value={phone} onChangeText={setPhone} keyboardType="phone-pad" />
      <TextInput style={styles.input} placeholder="Password" placeholderTextColor="#888" value={password} onChangeText={setPassword} secureTextEntry />

      <TouchableOpacity style={styles.button} onPress={handleSignUp}>
        <Text style={styles.buttonText}>Create Account</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={() => navigation.replace('Login')}>
        <Text style={styles.link}>Already have an account? Log In</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000', alignItems: 'center', justifyContent: 'center', paddingHorizontal: 24 },
  title: { fontSize: 28, color: '#00ffff', marginBottom: 20, fontWeight: '700' },
  input: { width: '100%', backgroundColor: '#1e1e1e', color: '#f5f5f5', padding: 12, borderRadius: 8, marginBottom: 12 },
  button: { backgroundColor: '#00ffff', paddingVertical: 12, paddingHorizontal: 20, borderRadius: 8, marginTop: 8, alignItems: 'center' },
  buttonText: { color: '#000', fontWeight: '700' },
  link: { color: '#f5f5f5', marginTop: 16 },
});