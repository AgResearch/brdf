--
-- Name: displayprocedureob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE displayprocedureob FROM PUBLIC;
REVOKE ALL ON TABLE displayprocedureob FROM agrbrdf;
GRANT ALL ON TABLE displayprocedureob TO agrbrdf;
GRANT SELECT ON TABLE displayprocedureob TO gbs;


--
-- Name: keyfile_factidseq; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON SEQUENCE keyfile_factidseq FROM PUBLIC;
REVOKE ALL ON SEQUENCE keyfile_factidseq FROM agrbrdf;
GRANT ALL ON SEQUENCE keyfile_factidseq TO agrbrdf;
GRANT SELECT ON SEQUENCE keyfile_factidseq TO gbs;


