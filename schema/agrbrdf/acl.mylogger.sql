--
-- Name: mylogger; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE mylogger FROM PUBLIC;
REVOKE ALL ON TABLE mylogger FROM agrbrdf;
GRANT ALL ON TABLE mylogger TO agrbrdf;
GRANT SELECT ON TABLE mylogger TO gbs;


--
-- Name: ob_obidseq; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON SEQUENCE ob_obidseq FROM PUBLIC;
REVOKE ALL ON SEQUENCE ob_obidseq FROM agrbrdf;
GRANT ALL ON SEQUENCE ob_obidseq TO agrbrdf;
GRANT SELECT,UPDATE ON SEQUENCE ob_obidseq TO gbs;


