--
-- Name: lisafanseriesnormalisation_backup23092008; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE lisafanseriesnormalisation_backup23092008 FROM PUBLIC;
REVOKE ALL ON TABLE lisafanseriesnormalisation_backup23092008 FROM agrbrdf;
GRANT ALL ON TABLE lisafanseriesnormalisation_backup23092008 TO agrbrdf;
GRANT SELECT ON TABLE lisafanseriesnormalisation_backup23092008 TO gbs;


--
-- Name: listorderseq; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON SEQUENCE listorderseq FROM PUBLIC;
REVOKE ALL ON SEQUENCE listorderseq FROM agrbrdf;
GRANT ALL ON SEQUENCE listorderseq TO agrbrdf;
GRANT SELECT,UPDATE ON SEQUENCE listorderseq TO gbs;


--
-- Name: lmf_factidseq; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON SEQUENCE lmf_factidseq FROM PUBLIC;
REVOKE ALL ON SEQUENCE lmf_factidseq FROM agrbrdf;
GRANT ALL ON SEQUENCE lmf_factidseq TO agrbrdf;
GRANT SELECT ON SEQUENCE lmf_factidseq TO gbs;


