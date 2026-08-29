using System.Linq;
using UnityEngine;

public sealed class LineExporter : MonoBehaviour
{
    [SerializeField] private string[] input;

    public string Export()
    {
        return string.Join("\n", input.Where(line => !string.IsNullOrWhiteSpace(line))) + "\n\n";
    }
}
