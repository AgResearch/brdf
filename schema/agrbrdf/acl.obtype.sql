--
-- Name: obtype; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE obtype FROM PUBLIC;
REVOKE ALL ON TABLE obtype FROM agrbrdf;
GRANT ALL ON TABLE obtype TO agrbrdf;
GRANT SELECT ON TABLE obtype TO gbs;


--
-- Name: obtype_obtypeidseq; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON SEQUENCE obtype_obtypeidseq FROM PUBLIC;
REVOKE ALL ON SEQUENCE obtype_obtypeidseq FROM agrbrdf;
GRANT ALL ON SEQUENCE obtype_obtypeidseq TO agrbrdf;
GRANT SELECT ON SEQUENCE obtype_obtypeidseq TO gbs;


