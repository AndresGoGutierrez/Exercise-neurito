"""Experimentos del taller de Neurito.

Usa el mismo entrenamiento de main.py (semilla 42, mismos datos), pero sin
pygame, y deja cambiar el tamaño de la capa oculta, las épocas y la tasa.
Se ejecuta con:  python experimentos.py
"""
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

actions =("comer", "dormir", "jugar")


def relu(values):
    return np.maximum(0, values)


def softmax(values):
    exp_values = np.exp(values - np.max(values, axis=1, keepdims=True))
    return exp_values / np.sum(exp_values, axis=1, keepdims=True)


def policy(data):
    # Prioridades: hambre, cansancio (1 - energía) y aburrimiento.
    return np.argmax(
        np.column_stack((data[:, 0], 1 - data[:, 1], data[:, 2])), axis=1
    )


def train(hidden_size=6, epochs=1200, lr=0.1, verbose=False):
    np.random.seed(42)
    X = np.random.rand(3000, 3)
    targets = policy(X)
    W1 = np.random.randn(3, hidden_size) * 0.5
    b1 = np.zeros((1, hidden_size))
    W2 = np.random.randn(hidden_size, 3) * 0.5
    b2 = np.zeros((1, 3))
    losses = []

    for epoch in range(epochs):
        z1 = X @ W1 + b1
        hidden = relu(z1)
        probabilities = softmax(hidden @ W2 + b2)
        count = len(X)
        loss = -np.mean(np.log(probabilities[np.arange(count), targets] + 1e-10))
        losses.append(loss)
        delta2 = probabilities.copy()
        delta2[np.arange(count), targets] -= 1
        delta2 /= count
        grad_W2 = hidden.T @ delta2
        grad_b2 = np.sum(delta2, axis=0, keepdims=True)
        delta1 = (delta2 @ W2.T) * (z1 > 0)
        grad_W1 = X.T @ delta1
        grad_b1 = np.sum(delta1, axis=0, keepdims=True)
        W1 -= lr * grad_W1
        b1 -= lr * grad_b1
        W2 -= lr * grad_W2
        b2 -= lr * grad_b2
        if verbose and epoch % 200 == 0:
            print(f"  época {epoch} | pérdida {loss:.4f}")

    def predict(data):
        return softmax(relu(data @ W1 + b1) @ W2 + b2)

    test = np.random.rand(1000, 3)
    test_targets = policy(test)
    accuracy = np.mean(np.argmax(predict(test), axis=1) == test_targets)
    return predict, losses, accuracy, test, test_targets


def show(predict, title, cases):
    print(title)
    for case in cases:
        probs = predict(np.array([case]))[0]
        name = actions[int(np.argmax(probs))]
        pct = " / ".join(f"{p * 100:5.1f}" for p in probs)
        print(f"  {case} -> {name:6s} ({pct})  [comer / dormir / jugar]")


def main():
    print("== Base: 6 neuronas, 1200 épocas, tasa 0.1 ==")
    predict, losses, accuracy, test, test_targets = train(verbose=True)
    print(f"pérdida final {losses[-1]:.4f} | precisión {accuracy:.2%}")
    reparto = np.bincount(test_targets) / len(test_targets)
    print("reparto de clases en el test:", np.round(reparto, 3))

    steps = [round(v * 0.1, 1) for v in range(11)]
    print("\n== Experimento 1: dos necesidades fijas, una cambia ==")
    show(predict, "Hambre cambia (energía 0.5, aburrimiento 0.3)",
         [[h, 0.5, 0.3] for h in steps])
    show(predict, "Energía cambia (hambre 0.3, aburrimiento 0.3)",
         [[0.3, e, 0.3] for e in steps])
    show(predict, "Aburrimiento cambia (hambre 0.3, energía 0.8)",
         [[0.3, 0.8, a] for a in steps])

    print("\n== Experimento 2: prioridades casi iguales ==")
    # Hambre 0.70 y cansancio 0.20 fijos; el aburrimiento sube hasta pasar al hambre.
    show(predict, "Aburrimiento cerca del hambre (hambre 0.7, energía 0.8)",
         [[0.7, 0.8, a] for a in (0.4, 0.6, 0.69, 0.70, 0.71, 0.75, 0.9)])
    show(predict, "Las tres prioridades iguales", [[0.5, 0.5, 0.5]])

    print("\n== Experimento 3: neuronas en la capa oculta ==")
    for size in (3, 6, 10, 20):
        _, losses, accuracy, _, _ = train(hidden_size=size)
        print(f"  {size:2d} neuronas | pérdida {losses[-1]:.4f} | precisión {accuracy:.2%}")

    print("\n== Experimento 4a: épocas ==")
    for epochs in (50, 200, 600, 1200, 3000):
        _, losses, accuracy, _, _ = train(epochs=epochs)
        print(f"  {epochs:4d} épocas | pérdida {losses[-1]:.4f} | precisión {accuracy:.2%}")

    print("\n== Experimento 4b: tasa de aprendizaje ==")
    for lr in (0.001, 0.01, 0.1, 1.0, 5.0, 20.0):
        with np.errstate(all="ignore"):
            _, losses, accuracy, _, _ = train(lr=lr)
        print(
            f"  tasa {lr:6} | pérdida {losses[-1]:.4f} | precisión {accuracy:.2%}"
            f" | pérdida máxima {max(losses):.2f}"
        )

    print("\n== Precisión engañosa: dónde falla la red base ==")
    predict, _, _, test, test_targets = train()
    predicted = np.argmax(predict(test), axis=1)
    errors = predicted != test_targets
    priorities = np.sort(
        np.column_stack((test[:, 0], 1 - test[:, 1], test[:, 2])), axis=1
    )
    margin = priorities[:, 2] - priorities[:, 1]  # distancia entre las dos prioridades más altas
    confidence = predict(test).max(axis=1)
    print(f"  errores: {errors.sum()} de {len(test)}")
    print(f"  diferencia entre las 2 prioridades más altas en los errores: máx {margin[errors].max():.3f}")
    print(f"  confianza promedio: aciertos {confidence[~errors].mean():.2f} | errores {confidence[errors].mean():.2f}")


if __name__ == "__main__":
    main()
