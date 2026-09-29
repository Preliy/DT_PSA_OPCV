using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;
using UnityEngine.UIElements;

namespace Preliy.Launcher
{
    /// <summary>
    /// Hides and shows every UI element in the running scene with a hot key (F4 by default).
    /// Created once at startup and kept across scene loads, so every scene gets it without being edited.
    /// </summary>
    public class UIVisibilityToggle : MonoBehaviour
    {
        private const Key TOGGLE_KEY = Key.F4;

        private bool _hidden;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            var instance = new GameObject(nameof(UIVisibilityToggle));
            instance.AddComponent<UIVisibilityToggle>();
            DontDestroyOnLoad(instance);
        }

        private void OnEnable() => SceneManager.sceneLoaded += OnSceneLoaded;

        private void OnDisable() => SceneManager.sceneLoaded -= OnSceneLoaded;

        private void Update()
        {
            var keyboard = Keyboard.current;
            if (keyboard == null || !keyboard[TOGGLE_KEY].wasPressedThisFrame) return;

            _hidden = !_hidden;
            Apply();
        }

        // A new scene always starts with its UI visible, so a hidden launcher never carries into a demo
        private void OnSceneLoaded(Scene scene, LoadSceneMode mode) => _hidden = false;

        private void Apply()
        {
            // Hide the root rather than disabling the UIDocument: disabling rebuilds the visual tree
            // and drops every element the OC managers added to it at startup
            foreach (var document in FindObjectsByType<UIDocument>(FindObjectsSortMode.None))
            {
                var root = document.rootVisualElement;
                if (root == null) continue;
                root.style.display = _hidden ? DisplayStyle.None : DisplayStyle.Flex;
            }

            foreach (var canvas in FindObjectsByType<Canvas>(FindObjectsSortMode.None))
            {
                if (!canvas.isRootCanvas) continue;
                canvas.enabled = !_hidden;
            }
        }
    }
}
