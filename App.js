import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, Text, View, Animated, Dimensions, TouchableOpacity } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import Profile from './screens/Profile';
import Login from './screens/Login';
import SignUp from './screens/SignUp';

const Stack = createNativeStackNavigator();

function SplashScreen({ navigation, route }) {
  const [displayText, setDisplayText] = useState('');
  const fullText = 'Lekh.AI';
  const screenWidth = Dimensions.get('window').width;

  const scaleAnim = useRef(new Animated.Value(1)).current;
  const opacityAnim = useRef(new Animated.Value(1)).current;
  const welcomeOpacity = useRef(new Animated.Value(0)).current;
  const welcomeY = useRef(new Animated.Value(0)).current;
  const elementsOpacity = useRef(new Animated.Value(0)).current;

  const firstName = route?.params?.firstName;

  useEffect(() => {
    let index = 0;
    const interval = setInterval(() => {
      index++;
      setDisplayText(fullText.slice(0, index));
      if (index === fullText.length) {
        clearInterval(interval);

        Animated.parallel([
          Animated.timing(scaleAnim, { toValue: 2, duration: 1000, useNativeDriver: true }),
          Animated.timing(opacityAnim, { toValue: 0, duration: 1000, useNativeDriver: true }),
        ]).start(() => {
          // First-time user → SignUp
          if (!firstName) {
            navigation.replace('SignUp');
          } else {
            // Show welcome dashboard, do NOT auto-navigate to Profile
            Animated.timing(welcomeOpacity, { toValue: 1, duration: 800, useNativeDriver: true }).start(() => {
              Animated.timing(welcomeY, { toValue: -250, duration: 1000, useNativeDriver: true }).start(() => {
                Animated.timing(elementsOpacity, { toValue: 1, duration: 600, useNativeDriver: true }).start();
              });
            });
          }
        });
      }
    }, 300);

    return () => clearInterval(interval);
  }, []);

  return (
    <View style={styles.container}>
      {/* Logo animation */}
      <Animated.Text style={[styles.title, { transform: [{ scale: scaleAnim }], opacity: opacityAnim }]}>
        {displayText}
      </Animated.Text>

      {/* Welcome dashboard */}
      {firstName && (
        <Animated.View style={{ opacity: welcomeOpacity, transform: [{ translateY: welcomeY }], alignItems: 'center' }}>
          <Text style={styles.welcome}>Welcome, {firstName}!</Text>
          <Animated.View style={{ opacity: elementsOpacity, alignItems: 'center' }}>
            <View style={styles.divider} />
            <View style={[styles.box, { width: screenWidth - 40 }]}>
              <Text style={styles.boxText}>1. First item</Text>
              <Text style={styles.boxText}>2. Second item</Text>
              <Text style={styles.boxText}>3. Third item</Text>
            </View>
          </Animated.View>
        </Animated.View>
      )}

      {/* Bottom bar with Profile button (static text) */}
      {firstName && (
        <Animated.View style={[styles.menuBar, { opacity: elementsOpacity }]}>
          {/* Use navigate (not replace) so Profile has a valid back stack */}
          <TouchableOpacity onPress={() => navigation.navigate('Profile', { firstName })}>
            <Text style={styles.menuText}>Profile</Text>
          </TouchableOpacity>
        </Animated.View>
      )}
    </View>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Splash" screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Splash" component={SplashScreen} />
        <Stack.Screen name="Profile" component={Profile} />
        <Stack.Screen name="Login" component={Login} />
        <Stack.Screen name="SignUp" component={SignUp} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000000', alignItems: 'center', justifyContent: 'center' },
  title: { fontSize: 40, fontWeight: 'bold', color: '#00ffff', position: 'absolute' },
  welcome: { fontSize: 32, fontWeight: '600', color: '#f5f5f5' },
  divider: { marginTop: 8, height: 2, backgroundColor: '#00ffff', width: 200 },
  box: { marginTop: 12, padding: 20, borderRadius: 12, backgroundColor: '#1e1e1e', alignItems: 'flex-start' },
  boxText: { fontSize: 20, color: '#f5f5f5', marginVertical: 6 },
  menuBar: { position: 'absolute', bottom: 0, width: '100%', height: 60, backgroundColor: '#1e1e1e', alignItems: 'center', justifyContent: 'center' },
  menuText: { fontSize: 20, color: '#00ffff', fontWeight: '500' },
});
