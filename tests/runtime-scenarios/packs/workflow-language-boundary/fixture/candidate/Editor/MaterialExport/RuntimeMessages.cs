using UnityEngine;

internal static class RuntimeMessages
{
    internal static void ReportMissingMaterial(string materialPath)
    {
        Debug.LogWarning($"Material is missing: {materialPath}. Return to Planner and update the canonical Owner.");
    }
}
