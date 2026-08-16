package org.qtycore.qt;

import android.os.Bundle;
import android.system.ErrnoException;
import android.system.Os;

import org.qtproject.qt5.android.bindings.QtActivity;

import java.io.File;

public class QTYQtActivity extends QtActivity
{
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        final File qtyDir = new File(getFilesDir().getAbsolutePath() + "/.qty");
        if (!qtyDir.exists()) {
            qtyDir.mkdir();
        }

        super.onCreate(savedInstanceState);
    }
}
