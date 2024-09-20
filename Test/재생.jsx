import React from 'react';
import { View, Image, StyleSheet } from 'react-native';

const App = () => {
  const videoStreamUrl = 'http://YOUR_SERVER_IP:8000/video_feed'; // FastAPI 서버의 URL

  return (
    <View style={styles.container}>
      <Image
        style={styles.video}
        source={{ uri: videoStreamUrl }}
        resizeMode="contain"
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  video: {
    width: '100%',
    height: '100%',
  },
});

export default App;
