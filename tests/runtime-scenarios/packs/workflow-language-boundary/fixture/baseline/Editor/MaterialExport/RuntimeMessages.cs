using UnityEngine;

internal static class RuntimeMessages
{
    internal static void ReportMissingMaterial(string materialPath)
    {
        Debug.LogWarning($"Material is missing: {materialPath}");
    }
}
