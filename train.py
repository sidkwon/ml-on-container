from tensorflow import keras
from sklearn.model_selection import train_test_split
import os

model_dir = '/opt/ml/model'

def train():
    # 패션 MNIST 데이터 불러오기
    (train_input, train_target), (test_input, test_target) = \
        keras.datasets.fashion_mnist.load_data()

    train_scaled = train_input.reshape(-1, 28, 28, 1) / 255.0

    train_scaled, val_scaled, train_target, val_target = train_test_split(
        train_scaled, train_target, test_size=0.2, random_state=42)

    # 합성곱 신경망 만들기
    model = keras.Sequential()
    model.add(keras.layers.Conv2D(32, kernel_size=3, activation='relu', 
                                  padding='same', input_shape=(28,28,1)))
    model.add(keras.layers.MaxPooling2D(2))
    model.add(keras.layers.Conv2D(64, kernel_size=(3,3), activation='relu', 
                                  padding='same'))
    model.add(keras.layers.MaxPooling2D(2))
    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(100, activation='relu'))
    model.add(keras.layers.Dropout(0.4))
    model.add(keras.layers.Dense(10, activation='softmax'))
    model.summary()

    # 모델 컴파일과 훈련
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', 
                  metrics=['accuracy'])

    checkpoint_cb = keras.callbacks.ModelCheckpoint(os.path.join(model_dir, 'best-cnn-model.h5'), 
                                                    save_best_only=True)
    early_stopping_cb = keras.callbacks.EarlyStopping(patience=2,
                                                      restore_best_weights=True)

    history = model.fit(train_scaled, train_target, epochs=1,
                        validation_data=(val_scaled, val_target),
                        callbacks=[checkpoint_cb, early_stopping_cb])

    model.evaluate(val_scaled, val_target)

    # 모델 저장
    #model.save_weights('model-weights.h5')
    model.save(os.path.join(model_dir, 'mnist', '1'))

if __name__ == '__main__':
    train()
