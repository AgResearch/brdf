--
-- Name: genotypestudy; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE genotypestudy FROM PUBLIC;
REVOKE ALL ON TABLE genotypestudy FROM agrbrdf;
GRANT ALL ON TABLE genotypestudy TO agrbrdf;
GRANT SELECT ON TABLE genotypestudy TO gbs;


