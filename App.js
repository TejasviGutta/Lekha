import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, Text, View, Animated, Dimensions } from 'react-native';

export default function App() {
  const [displayText, setDisplayText] = useState('');
  const fullText = 'Lekh.AI';

  const screenWidth = Dimensions.get('window').width;

  // Animations
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const opacityAnim = useRef(new Animated.Value(1)).current;
  const welcomeOpacity = useRef(new Animated.Value(0)).current;
  const welcomeY = useRef(new Animated.Value(0)).current;
  const elementsOpacity = useRef(new Animated.Value(0)).current; // one opacity for divider, box, menu

  useEffect(() => {
    let index = 0;
    const interval = setInterval(() => {
      index++;
      setDisplayText(fullText.slice(0, index));
      if (index === fullText.length) {
        clearInterval(interval);

        // Animate title zoom + fade out
        Animated.parallel([
          Animated.timing(scaleAnim, {
            toValue: 2,
            duration: 1000,
            useNativeDriver: true,
          }),
          Animated.timing(opacityAnim, {
            toValue: 0,
            duration: 1000,
            useNativeDriver: true,
          }),
        ]).start(() => {
          // Fade in Welcome text
          Animated.timing(welcomeOpacity, {
            toValue: 1,
            duration: 800, // faster fade
            useNativeDriver: true,
          }).start(() => {
            // Smooth slide upward
            Animated.timing(welcomeY, {
              toValue: -250,
              duration: 1000,
              useNativeDriver: true,
            }).start(() => {
              // Fade in divider, box, and menu bar together
              Animated.timing(elementsOpacity, {
                toValue: 1,
                duration: 600, // faster fade
                useNativeDriver: true,
              }).start();
            });
          });
        });
      }
    }, 300);

    return () => clearInterval(interval);
  }, []);

  return (
    <View style={styles.container}>
      {/* Title with typewriter + zoom/fade */}
      <Animated.Text
        style={[
          styles.title,
          { transform: [{ scale: scaleAnim }], opacity: opacityAnim },
        ]}
      >
        {displayText}
      </Animated.Text>

      {/* Welcome text that fades in then moves to top center */}
      <Animated.View
        style={{
          opacity: welcomeOpacity,
          transform: [{ translateY: welcomeY }],
          alignItems: 'center',
        }}
      >
        <Text style={styles.welcome}>Welcome, User!</Text>

        {/* Divider + Box fade in together */}
        <Animated.View style={{ opacity: elementsOpacity, alignItems: 'center' }}>
          <View style={styles.divider} />
          <View style={[styles.box, { width: screenWidth - 40 }]}>
            <Text style={styles.boxText}>1. First item</Text>
            <Text style={styles.boxText}>2. Second item</Text>
            <Text style={styles.boxText}>3. Third item</Text>
          </View>
        </Animated.View>
      </Animated.View>

      {/* Bottom menu bar fades in with divider + box */}
      <Animated.View style={[styles.menuBar, { opacity: elementsOpacity }]}>
        <View style={styles.menuItems}>
          <Text style={styles.menuText}>Settings</Text>
          <Text style={styles.menuText}>Profile</Text>
        </View>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#2c3e50',
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 40,
    fontWeight: 'bold',
    color: '#ecf0f1',
    position: 'absolute',
  },
  welcome: {
    fontSize: 32,
    fontWeight: '600',
    color: '#ecf0f1',
  },
  divider: {
    marginTop: 8,
    height: 2,
    backgroundColor: '#ecf0f1',
    width: 200,
  },
  box: {
    marginTop: 12,
    padding: 20,
    borderRadius: 12,
    backgroundColor: 'rgba(236, 240, 241, 0.2)',
    alignItems: 'flex-start',
  },
  boxText: {
    fontSize: 20,
    color: '#ecf0f1',
    marginVertical: 6,
  },
  menuBar: {
    position: 'absolute',
    bottom: 0,
    width: '100%',
    height: 60,
    backgroundColor: '#34495e',
    alignItems: 'center',
    justifyContent: 'center',
  },
  menuItems: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '60%',
  },
  menuText: {
    fontSize: 20,
    color: '#ecf0f1',
    fontWeight: '500',
    marginHorizontal: 20,
  },
});