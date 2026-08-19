using UnityEngine;

internal static class EnglishRuntimeLog
{
    internal static void ReportExportSize(int size)
    {
        Debug.LogWarning($"Material export size is invalid; fallback to {size}.");
    }
}
