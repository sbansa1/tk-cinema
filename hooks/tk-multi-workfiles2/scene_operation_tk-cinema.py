# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import c4d

import sgtk
from sgtk.platform.qt import QtGui

HookClass = sgtk.get_hook_baseclass()


__author__ = "Mykhailo Datsyk"
__contact__ = "https://www.linkedin.com/in/mykhailo-datsyk/"


class SceneOperation(HookClass):
    """
    Hook called to perform an operation with the
    current scene
    """

    def execute(
        self,
        operation,
        file_path,
        context,
        parent_action,
        file_version,
        read_only,
        **kwargs
    ):
        """
        Main hook entry point

        :param operation:       String
                                Scene operation to perform

        :param file_path:       String
                                File path to use if the operation
                                requires it (e.g. open)

        :param context:         Context
                                The context the file operation is being
                                performed in.

        :param parent_action:   This is the action that this scene operation is
                                being executed for.  This can be one of:
                                - open_file
                                - new_file
                                - save_file_as
                                - version_up

        :param file_version:    The version/revision of the file to be opened.
                                If this is 'None' then the latest version
                                should be opened.

        :param read_only:       Specifies if the file should be opened
                                read-only or not

        :returns:               Depends on operation:
                                'current_path' - Return the current scene
                                                 file path as a String
                                'reset'        - True if scene was reset to an
                                                 empty state, otherwise False
                                all others     - None
        """
        app = self.parent
        engine = app.engine

        app.log_debug("-" * 50)
        app.log_debug("operation: %s" % operation)
        app.log_debug("file_path: %s" % file_path)
        app.log_debug("context: %s" % context)
        app.log_debug("parent_action: %s" % parent_action)
        app.log_debug("file_version: %s" % file_version)
        app.log_debug("read_only: %s" % read_only)

        doc = c4d.documents.GetActiveDocument()

        if operation in ['open', 'save', 'save_as']:
            # Store the full Shotgun Context for the given file_path
            # This will be used by shotgun.pyp to ensure the correct
            # context is set when the c4d document is changed.
            engine.set_document_context(file_path, context)

        if operation == "current_path":
            return doc[c4d.DOCUMENT_FILEPATH]
        elif operation == "open":
            c4d.documents.LoadFile(file_path)
        elif operation == "save":
            c4d.documents.SaveDocument(
                doc,
                str(file_path),
                c4d.SAVEDOCUMENTFLAGS_NONE,
                c4d.FORMAT_C4DEXPORT
            ),
            c4d.documents.LoadFile(file_path)
        elif operation == "save_as":
            c4d.documents.SaveDocument(
                doc,
                str(file_path),
                c4d.SAVEDOCUMENTFLAGS_NONE,
                c4d.FORMAT_C4DEXPORT,
            )
            c4d.documents.LoadFile(file_path)
        elif operation == "reset":
            active = c4d.documents.GetActiveDocument()
            if active.GetChanged():
                response = c4d.gui.QuestionDialog(
                    'The active document has unsaved changes.\n'
                    'Would you like to save?'
                )
                if response:
                    active_name = doc.GetName()
                    active_path = doc.GetDocumentPath()
                    active_file_path = os.path.join(active_path, active_name)
                    c4d.documents.SaveDocument(
                        doc,
                        active_file_path or '',
                        (
                            c4d.SAVEDOCUMENTFLAGS_SAVEAS,
                            c4d.SAVEDOCUMENTFLAGS_NONE
                        )[bool(active_file_path)],
                        c4d.FORMAT_C4DEXPORT,
                    )

            new_doc = c4d.documents.BaseDocument()
            new_doc.SetDocumentName('Untitled')
            c4d.documents.InsertBaseDocument(new_doc)
            c4d.documents.SetActiveDocument(new_doc)
            return True
        elif operation == 'prepare_new':
            # TODO: Prepare new file...
            pass
